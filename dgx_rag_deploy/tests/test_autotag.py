import asyncio
import sys
import types
import unittest
from unittest.mock import patch

# The local lightweight test environment does not install every optional RAG
# dependency. Production imports the real mmh3 package from requirements.txt.
sys.modules.setdefault("mmh3", types.SimpleNamespace(hash=lambda value, signed=False: hash(value)))
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))

import rag_service
from modules import metadata
from modules import ui_helpers


class MetadataAutotagTests(unittest.TestCase):
    def test_snippet_samples_head_and_tail(self):
        text = "A" * 100 + "B" * 100 + "C" * 100
        snippet = metadata.build_autotag_snippet(text, max_chars=100)

        self.assertIn("A" * 50, snippet)
        self.assertIn("C" * 20, snippet)
        self.assertIn("middle omitted", snippet)
        self.assertNotIn("B" * 80, snippet)

    def test_normalize_autotag_result_enforces_schema(self):
        result = metadata.normalize_autotag_result({
            "doc_type": " Contract ",
            "date": "",
            "parties": "Acme Corp",
            "tags": ["Legal", "  Renewal  ", ""],
        })

        self.assertEqual(result["doc_type"], "contract")
        self.assertIsNone(result["date"])
        self.assertEqual(result["parties"], ["Acme Corp"])
        self.assertEqual(result["tags"], ["legal", "renewal"])
        self.assertEqual(result["summary"], "")

    def test_autotag_document_includes_filename_and_defaults(self):
        captured = {}

        def fake_chat(messages, chat_url, chat_model, chat_api_key, temperature=0.7, max_tokens=None):
            captured["prompt"] = messages[0]["content"]
            captured["chat_url"] = chat_url
            captured["chat_model"] = chat_model
            captured["chat_api_key"] = chat_api_key
            return '{"doc_type": "invoice"}'

        with patch.object(metadata, "_chat_completion", side_effect=fake_chat):
            result = metadata.autotag_document(
                "Invoice body",
                "http://autotag.local/v1/chat/completions",
                "AutotagModel",
                "secret",
                filename="invoice.pdf",
            )

        self.assertIn("Filename: invoice.pdf", captured["prompt"])
        self.assertEqual(captured["chat_url"], "http://autotag.local/v1/chat/completions")
        self.assertEqual(captured["chat_model"], "AutotagModel")
        self.assertEqual(captured["chat_api_key"], "secret")
        self.assertEqual(result, {
            "doc_type": "invoice",
            "date": None,
            "parties": [],
            "tags": [],
            "summary": "",
        })

    def test_autotag_retries_smaller_on_context_error(self):
        prompt_lengths = []

        def fake_chat(messages, chat_url, chat_model, chat_api_key, temperature=0.7, max_tokens=None):
            prompt_lengths.append(len(messages[0]["content"]))
            if len(prompt_lengths) == 1:
                raise RuntimeError("Context size has been exceeded.")
            return '{"doc_type": "report"}'

        with patch.object(metadata, "_chat_completion", side_effect=fake_chat):
            result = metadata.autotag_document(
                "A" * 3000,
                "http://autotag.local/v1/chat/completions",
                "AutotagModel",
                "secret",
                max_chars=800,
                filename="long.pdf",
            )

        self.assertEqual(result["doc_type"], "report")
        self.assertEqual(len(prompt_lengths), 2)
        self.assertLess(prompt_lengths[1], prompt_lengths[0])

    def test_clean_json_response_handles_fences_and_prose(self):
        fenced = metadata._clean_json_response('```json\n{"doc_type": "memo"}\n```')
        prose = metadata._clean_json_response('Here is the JSON:\n{"doc_type": "report"}\nDone.')

        self.assertEqual(fenced, '{"doc_type": "memo"}')
        self.assertEqual(prose, '{"doc_type": "report"}')

    def test_clean_json_response_reports_empty_or_malformed_output(self):
        with self.assertRaisesRegex(ValueError, "empty response"):
            metadata._clean_json_response("")
        with self.assertRaisesRegex(ValueError, "Raw response: no json here"):
            metadata._clean_json_response("no json here")

    def test_autotag_malformed_output_returns_default_metadata_with_error(self):
        with patch.object(metadata, "_chat_completion", return_value="not json"):
            result = metadata.autotag_document(
                "Document body",
                "http://autotag.local/v1/chat/completions",
                "AutotagModel",
                "secret",
            )

        self.assertEqual(result["doc_type"], "other")
        self.assertIn("_error", result)
        self.assertIn("Raw response", result["_error"])


class RagServiceAutotagTests(unittest.TestCase):
    def setUp(self):
        with rag_service._autotag_cache_lock:
            rag_service._autotag_cache.clear()

    def test_autotag_endpoint_uses_autotag_model_config_and_cache(self):
        calls = []

        def fake_autotag(markdown, url, model, key, max_chars, filename):
            calls.append((markdown, url, model, key, max_chars, filename))
            return {"doc_type": "memo", "date": None, "parties": [], "tags": ["ops"], "summary": "Done"}

        async def run_twice():
            with (
                patch.object(rag_service, "AUTOTAG_MODEL_URL", "http://autotag/v1/chat/completions"),
                patch.object(rag_service, "AUTOTAG_MODEL_NAME", "AutotagModel"),
                patch.object(rag_service, "AUTOTAG_API_KEY", "autotag-key"),
                patch.object(rag_service, "AUTOTAG_MAX_CHARS", 800),
                patch.object(rag_service, "autotag_document", side_effect=fake_autotag),
            ):
                first = await rag_service.autotag_endpoint(
                    api_key="test_key_0000",
                    markdown_content="memo text",
                    filename="memo.md",
                )
                second = await rag_service.autotag_endpoint(
                    api_key="test_key_0000",
                    markdown_content="memo text",
                    filename="memo.md",
                )
            return first, second

        first, second = asyncio.run(run_twice())

        self.assertEqual(first["metadata"], second["metadata"])
        self.assertFalse(first["telemetry"]["cache_hit"])
        self.assertTrue(second["telemetry"]["cache_hit"])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0], (
            "memo text",
            "http://autotag/v1/chat/completions",
            "AutotagModel",
            "autotag-key",
            800,
            "memo.md",
        ))

    def test_autotag_batch_returns_per_document_results(self):
        async def fake_autotag(markdown, filename=""):
            return {
                "metadata": {"doc_type": "other", "date": None, "parties": [], "tags": [filename], "summary": markdown},
                "telemetry": {"elapsed_seconds": 0.01, "cache_hit": False, "sample_chars": len(markdown), "model": "test"},
            }

        async def run_batch():
            with patch.object(rag_service, "_autotag_async", side_effect=fake_autotag):
                return await rag_service.autotag_batch_endpoint(
                    api_key="test_key_0000",
                    documents=[
                        {"filename": "a.md", "markdown_content": "A"},
                        {"filename": "missing.md"},
                        {"filename": "b.md", "markdown_content": "B"},
                    ],
                    concurrency=2,
                )

        result = asyncio.run(run_batch())

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["documents"], 3)
        self.assertEqual([item["status"] for item in result["results"]], ["ok", "error", "ok"])
        self.assertEqual(result["results"][0]["metadata"]["tags"], ["a.md"])
        self.assertEqual(result["results"][1]["error"], "No markdown_content provided")


class RagServiceCacheAndStreamingTests(unittest.TestCase):
    def test_cache_key_includes_filters_and_retrieval_settings(self):
        base = rag_service._cache_key("query", "collection", 10, {"doc_type": "invoice"}, False, False, False, "sys")

        self.assertNotEqual(base, rag_service._cache_key("query", "collection", 10, {"doc_type": "contract"}, False, False, False, "sys"))
        self.assertNotEqual(base, rag_service._cache_key("query", "collection", 10, {"doc_type": "invoice"}, True, False, False, "sys"))
        self.assertNotEqual(base, rag_service._cache_key("query", "collection", 10, {"doc_type": "invoice"}, False, True, False, "sys"))
        self.assertNotEqual(base, rag_service._cache_key("query", "collection", 10, {"doc_type": "invoice"}, False, False, True, "sys"))
        self.assertNotEqual(base, rag_service._cache_key("query", "collection", 10, {"doc_type": "invoice"}, False, False, False, "other"))

    def test_streaming_chat_honors_auto_extract_filters(self):
        captured = {}

        def fake_retrieve(query, client, collection, embed_url, embed_model, embed_key, top_k, filters):
            captured["filters"] = filters
            return [0.1, 0.2], []

        async def run_stream():
            with (
                patch.object(rag_service, "_qclient", return_value=object()),
                patch.object(rag_service, "extract_filters_from_query", return_value={"doc_type": "invoice"}),
                patch.object(rag_service, "retrieve", side_effect=fake_retrieve),
            ):
                response = await rag_service.chat_stream(
                    api_key="test_key_0000",
                    query="find invoices",
                    collection="docs",
                    auto_extract_filters=True,
                    memory_enabled=False,
                )
                async for _ in response.body_iterator:
                    pass

        asyncio.run(run_stream())

        self.assertEqual(captured["filters"], {"doc_type": "invoice"})


class UiHelperTests(unittest.TestCase):
    def test_unique_upload_names_dedupes_case_insensitively(self):
        names = ui_helpers.unique_upload_names(["scan.pdf", "SCAN.pdf", "scan.pdf", "notes.txt"])

        self.assertEqual(names, ["scan.pdf", "SCAN (2).pdf", "scan (3).pdf", "notes.txt"])

    def test_text_direct_upload_detection_and_decoding(self):
        self.assertTrue(ui_helpers.is_text_direct_upload("contract.md"))
        self.assertTrue(ui_helpers.is_text_direct_upload("data.CSV"))
        self.assertFalse(ui_helpers.is_text_direct_upload("slides.pptx"))
        self.assertEqual(ui_helpers.decode_text_upload("hello".encode("utf-8")), "hello")


if __name__ == "__main__":
    unittest.main()
