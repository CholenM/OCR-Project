
<!-- SECTION: PAGE 1 -->
# BASIC ADDITIVE MANUFACTURING LABORATORY MANUAL

---

![image](image_1.png) Marsman Drysdale Foundation, Inc.

![image](image_2.png) ![image](image_3.png) ![image](image_4.png) ![image](image_5.png) ![image](image_6.png) ![image](image_7.png)

<!-- SECTION: PAGE 2 -->
# BASIC ADDITIVE MANUFACTURING LABORATORY MANUAL

![image](image_1.png) Marsman Drysdale Foundation, Inc.

![image](image_2.png) ![image](image_3.png) ![image](image_4.png) ![image](image_5.png) ![image](image_6.png) ![image](image_7.png)

## PROPONENTS

- ENGR. OTTOMAN MONTANI JR
- ENGR. JOHN KYL CORTEZ
- ENGR. DENISE CECILE ARMAMENTO
- JOHN CHOLEN MAKIGOD
- MOISES CLINT BALBUENA

1


Note: The image placeholders are used to represent the logos as they cannot be extracted as actual images in Markdown. In a real scenario, you would replace these with actual image URLs or paths.

<!-- SECTION: PAGE 3 -->
# Table of Contents

## Lessons

- Lesson 01: Introduction to Advanced Manufacturing 9
- Lesson 02: 3D Printing Technologies and Materials 19
- Lesson 03: Applications of Additive Manufacturing 33

## Laboratories

- Laboratory 01: Parametric Thinking - Digital Design Foundations 43
- Laboratory 02: Toolpath Logic - Translating Models into Layers 61
- Laboratory 03: Machine Readiness: Calibration and First Runs 77
- Laboratory 04: Performance Metrics: Evaluating First Prints 86
- Laboratory 05: Support Strategies - Designing for Overhangs 96
- Laboratory 06: Single-Part Fabrication 106
- Laboratory 07: Modular Fabrication: Multi-Part Assembly Printing 114
- Laboratory 08: Kinematic Prints: Motion in a Single Build 121
- Laboratory 09: Adaptive Resolution: Variable Layer Techniques 131
- Laboratory 10: Surface Engineering - Post-Processing for Quality 139

2

<!-- SECTION: PAGE 4 -->
# Foreword

<div style="display: flex; align-items: flex-start; gap: 20px;">
  ![image](image_1.png)
  <div>
    <strong>Fr. Karel S. San Juan, S.J.</strong><br>
    University President<br>
    <em>Ateneo de Davao University</em>
  </div>
</div>

Additive manufacturing, more commonly known as 3D printing, represents a profound shift in how we imagine, design, and build. It embodies the convergence of creativity, technology, and problem-solving, a synthesis that reflects the Ignatian ideal of forming persons who think critically, act creatively, and serve the greater good.

The *Basic Additive Manufacturing Laboratory Manual* strengthens Ateneo de Davao University’s efforts to integrate innovation and applied learning in science and engineering. It allows students to explore emerging technologies not as passive learners but as active creators and collaborators in shaping meaningful solutions for real-world challenges in Mindanao and beyond.

This initiative resonates with *Fortiores 2030*, the university’s strategic vision that calls for greater strength in collaboration, innovation, and social transformation. It embodies the spirit of education that seeks both technical excellence and human depth, where technology serves as a tool for inclusive growth and sustainable development.

May this manual nurture curiosity, reflection, and purpose in every learner who enters the world of digital fabrication, and may their work contribute to building a more humane and hopeful future.

*Ad majorem Dei gloriam.*

3

<!-- SECTION: PAGE 5 -->
# Foreword

<div style="display: flex; align-items: flex-start; gap: 20px;">
  ![image](image_1.png)
  <div>
    <strong>George M. Drysdale, Jr.</strong><br>
    Chairman and CEO, Marsman Drysdale Group<br>
    Trustee, Marsman Drysdale Foundation, Inc.
  </div>
</div>

The Marsman Drysdale Foundation, Inc. (MDFI) is proud to continue its partnership with the Department of Education – Davao de Oro, the Department of Science and Technology XI – PSTO Davao de Oro, and Ateneo de Davao University through Project P.R.I.M.E. (Partnership in Robotics and Intelligent Machines for Education).

Together, we share a vision of nurturing young minds and empowering teachers to thrive in a world driven by technology and innovation.

This 3D Printing Laboratory Manual is more than a guide—it is a tool for discovery. It represents our shared belief that *learning through technology can open new doors of creativity and possibility*. As part of the “Additive Manufacturing: 3D Modeling to 3D Printing” program, it will help educators inspire students to transform ideas into tangible innovations.

At MDFI, we believe that *education has the power to shape the future*—one lesson, one idea, one invention at a time. We are honored to stand beside our partners in building a generation that embraces change, leads with curiosity, and learns with purpose.

*To our teachers and learners:* may this manual spark your imagination, strengthen your skills, and nurture your passion for learning. May it remind you that *every great innovation begins with a single idea and the courage to explore it*.

4

<!-- SECTION: PAGE 6 -->
# Foreword

![image](image_1.png)

**Phoebe Gay L. Refamonte, CESO VI**  
Schools Division Superintendent

In this era of rapid technological advancement, the integration of robotics and automation into education is not merely an innovation—it is a necessity. This Robotics Manual, developed through the collaborative efforts of our dedicated partners in Project PRIME, serves as a vital tool in equipping our learners in Davao de Oro with the *knowledge, creativity, and problem-solving skills* required to thrive in a digital and interconnected world.

The Department of Education – Davao de Oro Division is deeply committed to fostering a *culture of innovation and 21st-century learning*. Through this manual, students are empowered to explore the fascinating world of robotics in ways that encourage curiosity, critical thinking, and collaboration. It stands as a testament to our collective mission of nurturing learners who are not only technologically skilled but also values-driven and future-ready.

We extend our heartfelt gratitude to Project PRIME and all our education partners for their steadfast support and visionary contribution to this endeavor. May this manual inspire both teachers and students to pursue excellence, embrace innovation, and build a brighter, smarter Davao de Oro—one creative mind at a time.

5

<!-- SECTION: PAGE 7 -->
# Foreword

**Engr. Laarnie D. Albacite**  
OIC-Provincial Science and Technology Director  
*DOST XI-Provincial Science and Technology Office of Davao de Oro*

To our Partners in Innovation- Our Learners and Teachers,

We stand at a unique moment where the tools of advanced manufacturing are becoming accessible to everyone. This Basic Additive Manufacturing Laboratory Manual is more than just a resource; it is the blueprint for harnessing that power.

Developed through Project P.R.I.M.E. (Partnership in Robotics and Intelligent Machines for Education), this manual represents our shared commitment to equipping you with the critical, hands-on skills needed to thrive in a rapidly evolving, technology-driven world.

To our Learners: We challenge you to look beyond the two dimensions of a screen and step into the three-dimensional world of creation. Think of 3D printing not as a machine, but as an extension of your mind. Use this knowledge to prototype solutions, invent new tools, and transform your wildest ideas into tangible reality. Be designers. Be builders. Be innovators.

To our Teachers: Your role in translating these technical lessons into engaging, meaningful experiences is paramount. Thank you for championing this frontier, inspiring curiosity, and guiding our students to become the architects of tomorrow.

Let us embark on this journey with enthusiasm, knowing that *every object printed is a testament to the power of education and the limitless potential within our classrooms*.

6

<!-- SECTION: PAGE 8 -->
# Acknowledgment

The authors wish to extend their deepest gratitude to all the individuals and institutions who contributed to the development of this manual.

Special thanks to the Marsman Drysdale Foundation, Inc., the Department of Education (DepEd), and the Department of Science and Technology (DOST) - Davao de Oro for their continued support in advancing STEM and Technical-Vocational education in the Philippines.

We would also like to acknowledge the Ateneo de Davao University Research Council and School of Engineering and Architecture - Robotics Engineering Department for their invaluable support and for providing the laboratory facilities that made the creation and validation of these lessons possible.

To the educators and students who will receive this manual, may you treat it with commitment and curiosity as you explore the world of digital manufacturing.

This manual is dedicated to **all Filipino learners who continue to explore, innovate, and build the future of manufacturing**.

Your journey in creation begins here.

7

<!-- SECTION: PAGE 9 -->
# About this Manual

The Basic Additive Manufacturing Laboratory Manual is designed to introduce learners to the principles, technologies, and practical applications of Additive Manufacturing (AM), more commonly known as 3D printing. This manual serves as a structured guide for both instructors and students in conducting hands-on laboratory exercises that develop design thinking, digital fabrication skills, and an understanding of modern manufacturing processes.

Developed through the collaboration of the Marsman Drysdale Foundation, Inc., the Department of Education (DepEd), the Department of Science and Technology (DOST)-Davao de Oro, and the Ateneo de Davao University-Robotics Engineering Department, this manual bridges theoretical learning and real-world industry practices. Each lesson builds on foundational concepts, leading learners from digital model creation to physical prototyping using 3D printing technology.

## Disclaimer

This manual is intended solely for educational and instructional purposes.

While every effort has been made to ensure the accuracy of the information contained herein, the authors and institutions involved make no warranties or representations regarding completeness or suitability for any particular purpose. Users must observe proper laboratory safety protocols and manufacturer guidelines when operating equipment.

Unauthorized reproduction or distribution of this material, in whole or in part, is strictly prohibited without written permission from the authors

## Digital Resources

To enhance your learning experience and support all laboratory activities, supplementary materials and project files are available online.

You may access all resources by scanning the QR code below or visiting the provided Google Drive link.

![image](image_1.png)

8

<!-- SECTION: PAGE 10 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Alameda de Dania University, Roanoke Ave. Publication District, Dania City, 8000 Dania, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Course Title</th>
    <td>Basic Additive Manufacturing Laboratory Manual (3D Printing)</td>
  </tr>
  <tr>
    <th>Lesson No. and Title</th>
    <td>Lesson 01: Introduction to Advanced Manufacturing</td>
  </tr>
  <tr>
    <th>Learning Outcomes</th>
    <td>
      1. Identify the different manufacturing processes.<br>
      2. Describe the process of the different methods of manufacturing.<br>
      3. Compare the three manufacturing processes and determine best fit for specific project requirements.
    </td>
  </tr>
  <tr>
    <th>Time Frame</th>
    <td>This lesson can be finished in 1 HOUR.</td>
  </tr>
  <tr>
    <th>Introduction</th>
    <td>
      Hello learners! Before we explore the exciting world of 3D printing, let us first look at the bigger picture. Imagine you are designing something, maybe a phone stand, a toy robot, or a personalized keychain with your name on it. Before you can actually make that design real, you have to decide:<br><br>
      "How will I manufacture this?"<br><br>
      There are different ways to make things, and each method changes how your design looks, feels, and costs. The three main manufacturing methods are: <strong>Formative Manufacturing</strong> - shaping material using molds or pressure<br>
      <strong>Subtractive Manufacturing</strong> - cutting away material to form your object<br>
      <strong>Additive Manufacturing</strong> - building layer by layer, just like 3D printing.<br><br>
      By the end of this lesson, you will understand how each one works and when to use them because choosing the right process can make or break your design.
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

9

<!-- SECTION: PAGE 11 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Díaz University, Rojas Ave. Publication District, Díaz City, 8000 Díaz, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Lesson

### Formative Manufacturing

Let us begin with the most traditional method: *Formative Manufacturing*. Think of it like making chocolate in a mold. You melt the chocolate, pour it into a mold, wait a bit, and then you have a perfect shape.

*Formative manufacturing*

![image](image_5.png)

Formative manufacturing works the same way, but with plastics or metals. The material is melted, poured, or pressed into a mold and then cooled to form the desired part. Common examples include injection molding, casting, and forging.

**Example:** The plastic body of your TV remote or the casing of your mouse.

**How it works:** Melt → Shape → Cool → Remove.

**Advantages:**

- Perfect for mass production.
- Low cost per item once the mold is made.
- Produces smooth and uniform parts.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

10

<!-- SECTION: PAGE 12 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Drano University, Roes Ave. Publacion District, Drano City, 8000 Drano, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Disadvantages:

- Expensive tooling; molds cost a lot to make.
- Long setup time before production starts.
- Not ideal for custom or one-time products.

## Cost Analysis:

Formative manufacturing has **very high startup costs** but **very low cost per part** once production begins.

For example, making one mold might cost **₱50,000**, but if you use it to produce **10,000 items**, each item might only cost **₱10** to make. So, the more you produce, the cheaper each part becomes.

Formative manufacturing is perfect for making thousands of identical parts but not for small runs or experimental designs.

## Subtractive Manufacturing

Now imagine carving a wooden statue. You start with a solid block and carefully remove material until you get the final shape. That is *Subtractive Manufacturing*.

*Subtractive manufacturing*

![image](image_5.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

11

<!-- SECTION: PAGE 13 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Alameda de Dania University, Rodeo Ave. Publication District, Dania City, 8000 Dania, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

Instead of pouring material into a mold, we start with a solid block (metal, wood, or plastic) and use machines like CNC mills, lathes, or drills to remove what we do not need. CNC, stands for Computer Numerical Control, is largely responsible for the autonomous process of removing the unnecessary part in the subtractive manufacturing method.

## Examples:

- Metal engine parts
- Wooden furniture or metal prototypes

## How it works: Start with more → Cut away → End with precision.

## Advantages:

- Produces highly accurate and smooth parts.
- Works with almost any material, especially metals.
- Creates strong, functional products.

## Disadvantages:

- Wasteful, since a lot of material is removed.
- Tool access can limit complex shapes.
- Can be slow and costly for intricate designs.

## Cost Analysis:

Subtractive manufacturing has medium startup cost and medium cost per part.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

12

<!-- SECTION: PAGE 14 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave. Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## For example:

- One aluminum block might cost ₱500, but after cutting and polishing, the final piece might cost ₱800–₱1,000 because of tool wear and material waste.
- It is ideal for prototypes, small batches, or high-strength parts where precision matters more than volume.

In short, subtractive manufacturing balances accuracy and cost, but wastes material and time.

Subtractive manufacturing is like craftsmanship. It is precise, detailed, and perfect for strong parts, but not very efficient for complex or creative shapes.

---

## Additive Manufacturing

Finally, let us talk about the modern and most creative method: *Additive Manufacturing*, commonly known as *3D Printing*. Instead of removing or shaping materials, 3D printing builds up the part layer by layer from a digital model. It is like stacking LEGO bricks, but much more precise.

*Additive manufacturing*

![image](image_5.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

13

<!-- SECTION: PAGE 15 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

According to ISO/ASTM 52900:2015, additive manufacturing includes several categories such as:

- Material Extrusion (FFF or FDM) - melts filament layer by layer
- Vat Photopolymerization (SLA or DLP) - cures resin with light
- Powder Bed Fusion (SLS or DMLS) - fuses powder using lasers

Before we go deeper, it is important to note that the International Organization for Standardization (ISO) and American Society for Testing and Materials (ASTM) standards serve as the international guide for additive manufacturing. They define the terminology, classification, and process categories that help engineers, educators, and manufacturers speak a common technical language when working with 3D printing systems.

## Examples:

- Custom phone cases
- Dental models and hearing aids
- Drone parts or small robot prototypes

## Advantages:

- No molds or tooling needed
- Great for rapid prototyping and customization
- Can produce complex shapes that other methods cannot

## Disadvantages:

- Slower compared to mass production
- Material strength is lower than molded or machined parts

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

14

<!-- SECTION: PAGE 16 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Synthesis

- Limited build size and surface finish may need post-processing

### Cost Analysis:

Additive manufacturing has low startup cost but high cost per part for large-scale production.

For example: A single 3D printed keychain might cost ₱50 to ₱100 to make. Printing 100 pieces would still cost around ₱5,000 to ₱10,000 total because each print takes time.

It is perfect for custom parts, one-time designs, or prototypes, but not for thousands of copies.

Every object you see, may it be your gadgets, furniture, and even the tools in your classroom, was made using one or more of these three manufacturing methods.

<table>
  <thead>
    <tr>
      <th>Process</th>
      <th>How It Works</th>
      <th>Best For</th>
      <th>Limitation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Formative</td>
      <td>Material shaped using molds</td>
      <td>Mass production</td>
      <td>Expensive to start</td>
    </tr>
    <tr>
      <td>Subtractive</td>
      <td>Cuts away material</td>
      <td>Precision parts</td>
      <td>Material waste</td>
    </tr>
    <tr>
      <td>Additive</td>
      <td>Builds layer by layer</td>
      <td>Custom and prototype parts</td>
      <td>Slower build time</td>
    </tr>
  </tbody>
</table>

When deciding which method to use, remember:

- If you need **many identical parts**, choose **Formative**.
- If you need **strong and accurate parts**, choose **Subtractive**.
- If you need **unique, creative, or test models**, choose **Additive**.

Understanding cost, material, and purpose helps engineers and designers choose the right process for every situation.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

15

<!-- SECTION: PAGE 17 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Droo University, Roos Ave, Publication District, Droo City, 8000 Droo, Jl Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Reflection

Imagine you are creating a school project that needs a customized logo keychain for your robotics team. Would you choose Formative, Subtractive, or Additive manufacturing? Why is that the best choice in terms of cost, time, and quantity?

## FAQs

1. **What is the main difference between formative, subtractive, and additive manufacturing?**
   - Formative: Shapes material using molds or pressure.
   - Subtractive: Removes material from a solid block.
   - Additive: Builds parts layer by layer.
   - Each method has its own strengths, weaknesses, and cost considerations.

2. **Is 3D printing cheaper than other manufacturing methods?**
   - Not always. 3D printing is cheaper for small quantities and prototypes, but more expensive for mass production. Once you need hundreds or thousands of parts, formative manufacturing becomes much cheaper overall.

3. **Can one product use more than one manufacturing method?**
   - Yes! Many real products combine methods. For example, a drone might have a 3D-printed prototype frame (additive), machined metal arms (subtractive), and injection-molded propellers (formative).

4. **What should I consider when choosing a manufacturing process?**
   - You should consider: Quantity (how many parts you need), Material type, Strength requirements, Cost and time, Design complexity.

5. **Can I design something in CAD and use any method to make it?**

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

16

<!-- SECTION: PAGE 18 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Droo University, Roes Ave. Publication District, Droo City, 8000 Droo, Jl Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>References</th>
    <td>
      <ul>
        <li>Yes, but you may need to adjust your design depending on the process. For example, 3D printing allows hollow parts, but CNC machining might not. Formative processes may require draft angles or uniform thickness for molding.</li>
      </ul>
      <p>Ben Redwood, Filemon Schöffer, and Brian Garret, <em>The 3D Printing Handbook: Technologies, Design and Applications</em>. 3D Hubs B.V., Amsterdam, 2017.</p>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

17

<!-- SECTION: PAGE 19 -->

Local Engine Failed: HTTPConnectionPool(host='192.168.1.91', port=8000): Read timed out. (read timeout=120)


<!-- SECTION: PAGE 20 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Alameda de Dania University, Roanoke Ave. Publication District, Dania City, 8000 Dania, Del Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Course Title</th>
    <td>Basic Additive Manufacturing Laboratory Manual (3D Printing)</td>
  </tr>
  <tr>
    <th>Lesson No. and Title</th>
    <td>Lesson 02: 3D Printing Technologies and Materials</td>
  </tr>
  <tr>
    <th>Learning Outcomes</th>
    <td>
      1. Classify the process categories of 3D printing according to ISO/ASTM 52900 standards.<br>
      2. Differentiate the major 3D printing material groups and their properties.<br>
      3. Identify examples of material groups and their applications.<br>
      4. Evaluate the suitability of different technologies and materials based on accuracy, finish, cost, and post-processing requirements
    </td>
  </tr>
  <tr>
    <th>Time Frame</th>
    <td>This lesson can be finished in 1 HOUR and 30 MINUTES.</td>
  </tr>
  <tr>
    <th>Introduction</th>
    <td>
      When designing for 3D printing, one of the first big decisions you face is:<br>
      <strong>Which technology and material should I use?</strong><br>
      The truth is—there’s no single “best” choice. The answer depends on your application requirements: Do you need lightweight parts? High-temperature resistance? Smooth surface finish? Or maybe load-bearing strength?<br>
      Today, we will learn the different 3d printing technologies, the common materials associated with each technology, and their most common applications. By the end, you’ll understand why designers often say: “It’s not about the best material—it’s about the right material for the job.” Let’s start!
    </td>
  </tr>
  <tr>
    <th>Lesson</th>
    <td>
      In 2015, the ISO/ASTM 52900 Standard was created to standardize terminology and provide a framework for categorizing 3D printing methods. It established seven main process categories. Each category varies in process mechanics, applications, and material compatibility.
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

19

<!-- SECTION: PAGE 21 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Dania University, Rodeo Ave. Publication District, Dania City, 8000 Dania, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Material Groups

Just as technologies are categorized, materials in 3D printing are also grouped into major classes. Most fall under two broad categories: Polymers and Metals. Other specialized options include ceramic and composites.

### 3D PRINTING MATERIAL GROUPS

<table>
  <thead>
    <tr>
      <th>POLYMERS</th>
      <th>METALS</th>
      <th>OTHERS</th>
    </tr>
  </thead>
</table>


*Figure 2.1 3D Printing Material Groups*

---

## POLYMERS

Polymers are one of the most widely used materials in 3D printing and can be found in countless everyday applications—from adhesives to biomedical devices. In fact, the polymer industry is larger than the steel, aluminum, and copper industries combined.

In 3D printing, polymers can be understood in two different ways:

1) **Forms (Physical State)** - how the polymer is supplied and fed into the machine  
   a) **Filament** → solid spools used in extrusion-based printing (e.g., FFF/PLA).

![image](image_5.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

20

<!-- SECTION: PAGE 22 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td rowspan="2" style="background-color: #002868; width: 20%;"></td>
    <td>
      <p>b) Resin → liquid form used in photopolymerization processes (e.g., SLA/DLP).</p>
      <p>c) Powder → fine particles used in powder-based processes (e.g., SLS).</p>
      <p>2) Categories (Thermal Behavior) - how the polymer behaves under heat and curing.</p>
      <p>a) Thermoplastics → melt, solidify, and can be reheated without losing properties.</p>
      <p>Example: Bottles, LEGO bricks, packaging.</p>
      <p>b) Thermosets → cure permanently and cannot be remelted; instead, they degrade when reheated.</p>
      <p>Example: Epoxies, bowling balls, stove knobs.</p>
      <h3>METALS</h3>
      <p>Metals, unlike polymers, are almost exclusively used powders. Advantage is that it produces high-quality, functional, and load-bearing parts. This approach makes it possible to produce parts that are not only high in quality but also functional and capable of bearing heavy loads, making metals ideal for industrial applications.</p>
      ![image](image_5.png)
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

21

<!-- SECTION: PAGE 23 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## OTHER MATERIALS

Beyond polymers and metals, some 3D printing processes make use of ceramics and composites.

**Ceramics** are often created by filling polymers with ceramic powder. This combination provides improved wear resistance, which makes it especially useful for tooling applications. A good example can be seen in SLA printing, where ceramic powder-filled resin is used to produce high-detail injection molds.

**Composites** combine polymers with additives like chopped carbon, aluminum, graphite, or glass. These fillers enhance the base material, offering better strength-to-weight ratios, greater wear resistance, and even static resistance. In extrusion-based printing (FFF), exotic filaments such as wood-filled or metal-filled PLA have become popular, as they not only improve performance but also provide unique appearances that make printed parts stand out.

Now that we know the materials, the next question is: *How are these materials actually shaped into objects?* This is where the seven main process categories come in. Each process is optimized for certain materials. For example, thermoplastic filament is used in Material Extrusion (FFF), while resins are cured in Vat Photopolymerization (SLA/DLP). Metals, on the other hand, almost always rely on Powder Bed Fusion or Directed Energy Deposition. So, let’s now look at the technologies and see how they connect back to the materials we just discussed.”

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

22

<!-- SECTION: PAGE 24 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave. Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## TECHNOLOGIES

To better understand how these technologies are organized, the ISO/ASTM 52900 Standard presents a clear framework that divides all 3D printing methods into **seven main process categories**. Each process represents a different approach to building parts—whether by extruding melted filament, curing liquid resin, or fusing powders with heat. The diagram below provides a visual overview of these categories, along with their most common technologies. This serves as a ‘map of additive manufacturing’, helping us see where each process belongs before exploring them in detail.

### 3D Printing

<table>
  <tr>
    <td>Material Extrusion</td>
    <td>VAT Polymerization</td>
    <td>Powder Bed Fusion (Polymers)</td>
    <td>Material Jetting</td>
    <td>Binder Jetting</td>
    <td>Powder Bed Fusion (Metals)</td>
  </tr>
  <tr>
    <td>FFF</td>
    <td>SLA<br>DLP</td>
    <td>SLS</td>
    <td>Material Jetting<br>DOD</td>
    <td>Binder Jetting</td>
    <td>DMLS<br>SLM<br>EBM</td>
  </tr>
</table>

---

## Material Extrusion

Material extrusion is the **most common type of 3D printing**. It works like a **precise hot glue gun** — a plastic filament (like PLA or ABS) is melted in a heated nozzle and placed layer by layer until the object is complete.

### Common Issues:

- **Warping**: Parts bend if they cool unevenly.
- **Weak Layers**: Layers may not stick well and can crack.

### Advantages

- Low cost and easy to use
- Many colors and materials available

### Limitations

- Weaker along layer lines
- Visible layer marks on the surface

![image](image_5.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

23

<!-- SECTION: PAGE 25 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Drago University, Rojas Ave. Publication District, Drago City, 8000 Drago, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## VAT POYMERIZATION

### Common Applications

- Prototypes and Design Models
- Electronic Cases and Enclosures

Vat Photopolymerization is one of the **oldest and most precise** forms of 3D printing. This type of 3D printing uses **liquid resin** instead of plastic filament. A light hardens the resin layer by layer to create the object.

There are two main kinds:

- **SLA (Stereolithography)** – uses a laser to draw each layer.
- **DLP (Direct Light Processing)** – uses a projector to harden a whole layer at once.

After printing, the object is washed and cured under UV light to make it strong.

### Common Issues

- **Curling/warping** – large flat layers may shrink when cured, causing edges to curl.
- **Supports** – required for stability and can leave small marks on the surface.
- **Brittleness** – resins are less durable than standard plastics and may degrade over time.

### Advantages

- Very **high accuracy** and fine detail.
- Smooth surface finish (almost like injection-molded parts).

### Limitations

- Resin materials are **brittle** and not ideal for load-bearing parts.
- Prints require post-processing (washing and curing).

### Common Applications

- Visual prototypes and display models
- Jewelry (especially investment casting patterns).
- Dental models, crowns, and surgical guides.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

24

<!-- SECTION: PAGE 26 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## POWDER BED FUSION (POYLMERS)

Powder Bed Fusion uses a laser or heat to melt powder layers together to form an object. In plastics, it’s called Selective Laser Sintering (SLS) and often uses nylon powder. A big advantage is that the extra powder supports the object as it prints — no extra structures are needed! After printing, the extra powder is brushed off and reused.

![image](image_5.png)

### Common Issues

- **Warping/shrinkage** — parts may distort during cooling if temperature is uneven.
- **Surface finish** — parts have a grainy, matte texture that may need post-processing.
- **Powder handling** — fine powders require careful safety precautions.

### Advantages

- Strong, functional parts with excellent mechanical properties.
- No need for support structures (powder holds the shape).
- Good for complex geometries, ducts, and hollow sections.

### Limitations

- Industrial machines are expensive and require skilled operators.
- Long build times because of heating and cooling stages.

### Common Applications

- Functional prototypes and end-use parts.
- Complex ducting, piping, and hollow parts.
- Engineering applications require strong polymer components.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

25

<!-- SECTION: PAGE 27 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## MATERIAL JETTING MK/DOD

Material Jetting works like a 2D printer, but instead of ink, it sprays tiny droplets of liquid plastic or wax that harden with light. It builds objects layer by layer with very smooth and detailed surfaces—and can even print in different colors or materials at once!

![image](image_5.png)

### Common Issues

- **Support** - Requires support structures (printed from a separate material).
- **Costly** - Supports are printed solid, so they use a lot of material.
- **Accuracy** - Large parts may lose accuracy due to the shrinkage of the resins during curing.

### Advantages

- Best accuracy among 3D printing processes (layers as thin as 16 microns).
- Very smooth surface finish, close to injection-molded quality.
- Can print multi-material and full-color parts.

### Limitations

- High cost of machines and materials.
- Limited material range (mostly photopolymers).
- Wasteful support usage compared to other processes.

### Common Applications

- Full-color prototypes that look like the final product.
- Medical models for training and patient visualization.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

26

<!-- SECTION: PAGE 28 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Driano University, Roanoke Ave. Publication District, Driano City, 8000 Driano, Del Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## BINDER JETTING

Binder Jetting works like **gluing powder** together! A printer sprays a liquid binder onto thin layers of powder, sticking them to form the object. It prints at room temperature, so it’s **cheaper** and great for big parts. After printing, the extra powder is brushed off and reused, and the part may need to be heated or coated to make it stronger.

![image](image_5.png)

### Common Issues

- “Green State” - Parts are weak when first removed from the printer.
- Grainy Finish - Surface finish is usually grainy.
- Shrinkage - Can possibly shrink during sintering can affect accuracy.

### Advantages

- No heat → no warping or thermal stress.
- Low cost compared to laser-based methods.
- High material efficiency (unbound powder is 100% recyclable).

### Limitations

- Mechanical strength depends on post-processing.
- Not ideal for high-strength load-bearing parts without extra steps.

### Common Applications

- Full-color prototypes – realistic models for visualization.
- Functional metal parts – after sintering/infiltration, metal Binder Jetting can produce usable parts with complex shapes.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

27

<!-- SECTION: PAGE 29 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Drago University, Rojas Ave. Publication District, Drago City, 8000 Drago, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## POWDER BED FUSION (METALS)

Metal Powder Bed Fusion uses laser or electron beam to melt metal powder layer by layer, creating strong and detailed metal parts. It’s like SLS printing, but at much higher temperatures.

There are three main variations:

- **DMLS (Direct Metal Laser Sintering)** → heats metal alloy powders so they fuse at a molecular level (not fully melted).
- **SLM (Selective Laser Melting)** → fully melts single-metal powders (e.g., titanium) into a solid homogeneous part.
- **EBM (Electron Beam Melting)** → uses an electron beam instead of a laser; faster build speeds, but rougher surfaces and limited to conductive materials.

### Common Issues

- **Warping** - Residual stress and warping from extreme heat differences.
- **Support** - It requires support structures to anchor parts and manage heat.
- **Post-processing** - Cutting, heat treatment, polishing are usually needed.

### Advantages

- Produces parts with excellent mechanical properties
- High accuracy and detail (good for medical and aerospace).
- Uses well-known engineering metals (stainless steel, titanium, aluminum, cobalt-chrome).

### Limitations

- Very expensive (machines and powders).
- Requires skilled operators and strict safety procedures.
- Not cost-effective for simple or high-volume parts (like bolts or washers).

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

28

<!-- SECTION: PAGE 30 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Rodeo Ave, Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Synthesis

### Common Applications

- Medical → patient-specific implants, dental crowns, bone plates.
- Aerospace & Automotive → lightweight, optimized parts made of titanium or aluminum alloys.
- Engineering prototypes → highly customized, complex parts.

You’ve just completed Lesson 2: 3D Printing Technologies and Materials! To give you a summary, 3D printing offers a wide variety of methods and materials, each with unique strengths and limitations.

The seven main process categories (FFF, SLA/DLP, SLS, Material Jetting, Binder Jetting, DMLS/SLM, and EBM) can be grouped into those best for functional parts (SLS, DMLS/SLM) and those best for visual prototypes (SLA, Material Jetting). The choice of process depends on balancing cost, strength, accuracy, and appearance. As a rule of thumb:

- **For plastics**: use FFF for low-cost prototyping, or SLS for strong functional parts.
- **For visual/detail models**: choose SLA/DLP for affordability or Material Jetting for full-color and precision.
- **For metals**: Binder Jetting is cost-effective but weaker; DMLS/SLM gives the strongest, most precise parts but at a high cost.

This lesson highlights that there is no “best” 3D printing technology; rather, the right one is chosen for the specific application. Give yourself a pat on the back, you’ve unlocked the foundations of how designers and engineers decide what to print, how to print it, and with which material.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

29

<!-- SECTION: PAGE 31 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Driano University, Roanoke Ave. Publication District, Driano City, 8000 Driano, Del Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Reflection

In this lesson, we learned that every 3D printing technology and material has its own strengths, limitations, and purpose. Choosing the right one requires **discernment**. As innovators, we are called not just to seek what works but to choose what serves best. In every design we make, may we strive to become engineers for others, building not just objects, but hope and possibilities for a better world.

## FAQs

1. **Which 3D printing technology is the cheapest for students?**
   - Material Extrusion or FFF (Fused Filament Fabrication) where desktop printers are affordable, and filaments (like PLA) are low-cost.

2. **Which technology gives the strongest parts?**
   - DMLS/SLM (metal printing) produces the strongest functional parts, while SLS (nylon powder) is the strongest among polymers.

3. **Why do some prints need support?**
   - Supports hold up overhanging parts while printing. In FFF, SLA, and MJ, they are necessary. In SLS and Binder Jetting, the powder itself acts as support.

4. **Can 3D printed parts replace factory-made products?**
   - Sometimes, but not always. 3D printing is excellent for prototypes, custom parts, and low-volume production, but traditional manufacturing is still faster and cheaper for mass production.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

30

<!-- SECTION: PAGE 32 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Alameda de Drago University, Rojas Ave. Publication District, Drago City, 8000 Drago, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## REFERENCES

[1] Fillamentum, “Fillamentum DR3D Filament,” 3D Printing Industry, 2015. [Online]. Available: https://3dprintingindustry.com/news/fillamentum-dr3d-filament-37955/

[2] 3D Centroamerica, “Metal Composite 3D Printer Filament,” 3D Centroamerica, 2023. [Online]. Available: https://3dcentroamerica.com/misc/metal-composite-3d-printer-filament.html

[3] Simplify3D, “3D Printed PLA Filament,” Simplify3D Resources, 2019. [Online]. Available: https://www.simplify3d.com/wp-content/uploads/2019/04/3d-printed-pla-filament-1024x773-1024x773.jpg

[4] MetaPress, “4 Ways SLA 3D Printing Saves Dental Health,” MetaPress, 2023. [Online]. Available: https://metapress.com/4-ways-sla-3d-printing-saves-dental-health/

[5] Engineering Product Design, “Powder Bed Fusion,” Engineering Product Design Knowledge Base, 2022. [Online]. Available: https://engineeringproductdesign.com/knowledge-base/powder-bed-fusion/

[6] Tritech Titanium Parts, “Binder Jetting Technology,” Tritech Titanium Technologies, 2023. [Online]. Available: https://tritechtitanium.com/technologies/3d-printing/

[7] Ebeam Machine, “How to Design Parts for Powder Bed Fusion Printing,” Ebeam Machine, 2023. [Online]. Available: https://ebeammachine.com/how-to-design-parts-for-powder-bed-fusion-printing/

[8] All3DP, “What Is Material Jetting? 3D Printing Basics,” All3DP, 2023. [Online]. Available: https://all3dp.com/1/what-is-material-jetting-3d-printing-basics/

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

31

<!-- SECTION: PAGE 33 -->

Local Engine Failed: HTTPConnectionPool(host='192.168.1.91', port=8000): Read timed out. (read timeout=120)


<!-- SECTION: PAGE 34 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Rojas Ave. Publacion District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Course Title</th>
    <td>Basic Additive Manufacturing Laboratory Manual (3D Printing)</td>
  </tr>
  <tr>
    <th>Lesson No. and Title</th>
    <td>Lesson 03: Applications of Additive Manufacturing</td>
  </tr>
  <tr>
    <th>Learning Outcomes</th>
    <td>
      1. Identify key industries that use Additive Manufacturing (AM).<br>
      2. Describe specific applications of AM in at least five different industries.<br>
      3. Compare traditional manufacturing and additive manufacturing in terms of time, cost, and complexity.<br>
      4. Analyze real-world case studies where AM provided significant benefits.<br>
      5. Demonstrate understanding by presenting a brief analysis of a chosen AM application.
    </td>
  </tr>
  <tr>
    <th>Time Frame</th>
    <td>This lesson can be finished in 1 HOUR and 30 MINUTES.</td>
  </tr>
  <tr>
    <th>Introduction</th>
    <td>Hello learners! You already learned the 3D Printing processes, technologies and materials. This time you will learn the real-life applications of Additive Manufacturing in different industries.</td>
  </tr>
  <tr>
    <th>Lesson</th>
    <td>
      Additive Manufacturing (AM), more commonly known as 3D printing, is a modern manufacturing process where objects are built layer by layer from digital designs. While it was originally used mainly for prototyping, AM has evolved into a key production method across many industries—including aerospace, medical, automotive, fashion, construction, and more.<br><br>
      Today, companies use AM not just to test and visualize designs, but to create final, functional products such as aircraft components, customized implants, and even houses. Its ability to handle complex shapes, minimize material waste, and shorten production times has made it increasingly vital in modern manufacturing.<br><br>
      Here is the summary of the applications of 3D Printing in various industries. The table also presents the possible technologies used.
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

33

<!-- SECTION: PAGE 35 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave. Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <thead>
    <tr>
      <th>Industry</th>
      <th>Applications</th>
      <th>Technologies</th>
      <th>Key Benefits</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Robotics</td>
      <td>Custom robotic grippers and joints- Lightweight, complex frames and arms- Rapid prototyping of mechatronic parts- Soft robotics components- Custom sensor housings and actuator mounts</td>
      <td>FDM, SLS, SLA, PolyJet</td>
      <td>-Faster iteration and prototyping<br>-Enables complex geometries not possible with traditional methods<br>-Reduces part weight while maintaining structural integrity</td>
    </tr>
    <tr>
      <td>Aerospace & Automotive</td>
      <td>-Direct metal parts (e.g., titanium)- Lightweight parts for vehicles<br>-Rapid prototyping of components<br>- Casting patterns for impellers, engines<br>- Gearbox housing, engine blocks, wiper motor tools- 40% less material used compared to traditional processes</td>
      <td>EBM, SLS, SLA</td>
      <td>- 30–70% reduced lead time<br>- Up to 45% cost savings<br>-30–35% cost reduction in low-volume parts</td>
    </tr>
    <tr>
      <td>Artistic / Jewelry</td>
      <td>- Intricate jewelry patterns-</td>
      <td>SLA, Envisiontec, Solidscape</td>
      <td>- High resolution</td>
    </tr>
  </tbody>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

34

<!-- SECTION: PAGE 36 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Aleneo de Draco University, Rodeo Ave. Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td rowspan="4" style="background-color: #002868; color: white; width: 15%;"></td>
    <td></td>
    <td>Investment casting masters- Customized artistic products (e.g., brooches, figurines)- Reduced manual labor for molding</td>
    <td></td>
    <td>- Faster turnaround (hours vs days)<br>- Unique, complex designs easily fabricated</td>
  </tr>
  <tr>
    <td>Medical / Healthcare</td>
    <td>-Anatomical models from CT/MRI<br>- Custom implants, hearing aids- Surgical guides, bone scaffolds<br>- Dental implants and prosthetics</td>
    <td>SLA, SLS, FDM, 3DP</td>
    <td>-Enhanced surgical precision<br>- Patient-specific customization<br>- 95.7% success in jaw reconstruction case study<br>- Time and cost savings</td>
  </tr>
  <tr>
    <td>Architectural</td>
    <td>- Scale models of buildings- Conceptual designs with complex geometry- Easy revisions via CAD- Unique structures and facades</td>
    <td>SLA</td>
    <td>- Saves time over manual modeling<br>- Allows intricate, non-standard shapes<br>- Improves client communication</td>
  </tr>
  <tr>
    <td>Fashion / Footwear</td>
    <td>- Customized shoes, insoles, accessories- Avant-garde wearable designs- Complex clothing structures and 3D-printed fabrics</td>
    <td>SLS, FDM, PolyJet</td>
    <td>- Personalization and comfort<br>- Reduced waste and inventory<br>- Rapid design-to-production pipeline</td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

35

<!-- SECTION: PAGE 37 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave. Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td rowspan="3" style="background-color: #002868; color: white; width: 20%;"></td>
    <td>Construction</td>
    <td>-3D-printed houses, walls, bridges<br>- On-site printing of emergency shelters<br>-Complex geometries with reduced manual labor</td>
    <td>Concrete 3D Printing (e.g., Contour Crafting)</td>
    <td>- Reduced labor and material cost<br>- Fast building of structures<br>- Lower carbon footprint compared to traditional construction</td>
  </tr>
  <tr>
    <td>Consumer Goods</td>
    <td>- Customized products (toys, eyewear, home décor)- Small batch production of electronics casings, gadgets- Rapid prototyping for market testing</td>
    <td>FDM, SLA, SLS</td>
    <td>-Personalization<br>- Reduced time-to-market<br>- On-demand production reduces storage costs</td>
  </tr>
  <tr>
    <td>Food Industry</td>
    <td>- Custom-shaped chocolates, pasta, meat substitutes- Nutritionally tailored meals (e.g., for elderly or astronauts)- Aesthetic food designs</td>
    <td>Food-safe 3D Printing (e.g., extrusion, inkjet)</td>
    <td>- Creative, complex edible designs<br>- Personalized nutrition<br>- Reduces food waste</td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

36

<!-- SECTION: PAGE 38 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Alameda de Drago University, Rojas Ave. Publication District, Drago City, 8000 Drago, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td rowspan="4" style="background-color: #002868; color: white; vertical-align: top; padding: 20px;">
      <!-- Left column content -->
    </td>
    <th>Electronics</th>
    <td>- Printed circuit boards (PCBs)<br>- Embedded sensors and antennas-<br>Lightweight drone components</td>
    <td>Inkjet Printing, FDM with conductive materials</td>
    <td>- Miniaturization-<br>Integration of form and function<br>- Faster prototyping of devices</td>
  </tr>
  <tr>
    <th>Energy / Oil & Gas</th>
    <td>- Turbine blades, fuel nozzles- Heat exchangers-<br>Custom drilling components- Spare parts for remote locations</td>
    <td>DMLS, SLM, EBM</td>
    <td>-Improved performance through optimized geometries<br>- On-site manufacturing<br>- Reduces downtime and logistics cost</td>
  </tr>
  <tr>
    <th>Education & Research</th>
    <td>- Teaching aids (anatomical models, physics kits)-<br>Student prototyping for engineering/design<br>- Research into new materials and structures</td>
    <td>FDM, SLA, Binder Jetting</td>
    <td>-Enhances experiential learning<br>- Facilitates innovation and creativity<br>- Cost-effective experimentation</td>
  </tr>
  <tr>
    <th>Defense & Military</th>
    <td>- Spare parts in remote areas or battlefields-<br>Drones, weapon components</td>
    <td>SLS, DMLS, FDM</td>
    <td>- On-demand production near combat zones<br>-Reduces logistics and supply chain dependency</td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

37

<!-- SECTION: PAGE 39 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Ateneo de Davao University, Raros Ave. Publacion District, Davao City, 8000 Davao, Jl Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

The Ateneo de Davao University – Robotics Engineering program developed 3D Printed medical trainers, such as the IV arm, for the School of Nursing. In partnership with the Davao Medical School Foundation Inc., the department developed the Digital Sphygmomanometer. This helps medical professors effectively assess their students by measuring the patient's blood pressure.

![image](image_5.png) ![image](image_6.png)

**Figure 3.1 3D Printed IV Arm**

Now, let us compare the traditional manufacturing and additive manufacturing in terms of time, cost and complexity. See the table below.

<table>
  <thead>
    <tr>
      <th>Criteria</th>
      <th>Traditional Manufacturing</th>
      <th>Additive Manufacturing</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Time</td>
      <td>Long setup time (tooling, molds)<br>Slower for custom parts</td>
      <td>Fast prototyping and production</td>
    </tr>
  </tbody>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

38

<!-- SECTION: PAGE 40 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Raros Ave. Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td rowspan="2" style="background-color: #002868; color: white; padding: 20px; vertical-align: top;">
      <!-- Left column content -->
    </td>
    <td><strong>Cost</strong></td>
    <td>High initial costs (tooling, molds)<br>Cost-effective for mass production</td>
    <td>Ideal for rapid iteration<br>Low setup costs<br>More economical for low-volume or custom parts</td>
  </tr>
  <tr>
    <td><strong>Complexity</strong></td>
    <td>Limited by tooling and machining capabilities</td>
    <td>Can produce highly complex and organic geometries with ease</td>
  </tr>
  <tr>
    <td colspan="4" style="padding: 10px;">
      <em>Additive Manufacturing is capable of producing complex designs efficiently, saving both time and cost.</em>
    </td>
  </tr>
  <tr>
    <td><strong>Synthesis</strong></td>
    <td colspan="3">
      At this juncture, I would like to congratulate you on the job well done!<br>
      You have just explored the lesson 3 of Additive Manufacturing.<br><br>
      Remember these key takeaways:<br>
      <ul>
        <li>3D printing is notone-size-fits-all—its effectiveness depends on the chosen technology, material, and application.</li>
        <li>Customization, reduced waste, and design freedom make AM valuable for innovation.</li>
        <li>AM complements, rather than replaces, traditional manufacturing—together, they drive modern production.</li>
      </ul>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

39

<!-- SECTION: PAGE 41 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Dranco University, Roaros Ave. Publication District, Dranco City, 8000 Dranco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Reflection</th>
    <td>
      As future engineers, innovators, and designers, you now understand that Additive Manufacturing is more than a tool—it’s a mindset. It invites us to rethink how we create, build, and solve problems.<br><br>
      Think about this:
      <ul>
        <li>How can 3D printing empower industries in your community?</li>
        <li>What real-world problems could you solve through additive design?</li>
        <li>In what ways can you use AM to serve others or improve daily life?</li>
      </ul>
      Innovation begins with curiosity. As you continue learning, remember—every printed layer represents a step toward shaping a better world.
    </td>
  </tr>
  <tr>
    <th>FAQs</th>
    <td>
      <ol>
        <li>What is the most common industry using 3D printing today?
          <ul>
            <li>Aerospace and medical industries lead in using AM for both prototyping and production.</li>
          </ul>
        </li>
        <li>Can 3D printing replace traditional manufacturing?
          <ul>
            <li>Not entirely. It complements traditional methods, especially for low-volume, customized, or complex parts.</li>
          </ul>
        </li>
        <li>Is 3D printing expensive?
          <ul>
            <li>While materials can be costly, AM reduces expenses in tooling, labor, and production time—especially for customized products.</li>
          </ul>
        </li>
        <li>How is AM used in education?
          <ul>
            <li>It enhances hands-on learning by allowing students to design, prototype, and test physical models easily and affordably.</li>
          </ul>
        </li>
      </ol>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

40

<!-- SECTION: PAGE 42 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td>5. What’s the future of 3D printing?<br>○ The future lies in <em>multi-material printing, bioprinting, and on-site manufacturing</em> for construction and space exploration.</td>
  </tr>
  <tr>
    <td>References</td>
    <td>[1] R. K. S. S. Negi, “Basics, applications and future of additive manufacturing technologies: A review,” <em>Journal of Manufacturing Technology Research</em>, vol. 5, pp. 75–96, 2013.<br><br>[2] D. Godec, T. Breski, M. Katalenic, and A. Nordin, “Applications of AM,” in <em>A Guide to Additive Manufacturing</em>. ResearchGate, 2022, pp. 149–229.</td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

41

<!-- SECTION: PAGE 43 -->

Local Engine Failed: HTTPConnectionPool(host='192.168.1.91', port=8000): Read timed out. (read timeout=120)


<!-- SECTION: PAGE 44 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Droo University, Roanoke Ave, Publication District, Droo City, 8000 Droo, Jol Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Course Title</th>
    <td>Basic Additive Manufacturing Laboratory Manual (3D Printing)</td>
  </tr>
  <tr>
    <th>Lesson No. and Title</th>
    <td>Laboratory 01: Parametric Thinking - Digital Design Foundations</td>
  </tr>
  <tr>
    <th>Learning Outcomes</th>
    <td>
      1. Successfully navigate the TinkerCAD user interface and workplane.<br>
      2. Utilize basic tools to create, manipulate, and combine primitive 3D shapes.<br>
      3. Design and export a simple, personalized 3D model suitable for 3D printing.
    </td>
  </tr>
  <tr>
    <th>Time Frame</th>
    <td>This laboratory activity can be finished in 1 HOUR.</td>
  </tr>
  <tr>
    <th>Introduction</th>
    <td>
      ![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)<br>
      <strong>Figure 1: 3D Modeling Applications</strong><br><br>
      3D Modeling is the process of creating a three-dimensional digital representation of an object. While professional-grade software like Onshape, Solidworks, and Autodesk Fusion 360 offer powerful tools for complex engineering and design, they require significant training.<br><br>
      ![image](image_9.png) ![image](image_10.png)<br>
      <strong>Figure 1.1: Autodesk TinkerCAD</strong>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_11.png) ![image](image_12.png) ![image](image_13.png) ![image](image_14.png)

---

43

<!-- SECTION: PAGE 45 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Drago University, Rojas Ave. Publacion District, Drago City, 8000 Drago, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td>For this introductory lesson, we will utilize TinkerCAD. It is a browser-based application known for its simplicity and accessibility, making it the ideal starting point for anyone new to 3D modeling.</td>
  </tr>
  <tr>
    <td><strong>Lesson</strong></td>
    <td><strong>Part A: Getting Started and Navigating Your Workspace</strong></td>
  </tr>
  <tr>
    <td></td>
    <td><strong>Step 1: Open TinkerCAD:</strong> First, go to the TinkerCAD website and log in. Once you are logged in, click the "+ Create" button and select "3D Design" to open a new project.<br><br>![image](image_5.png)<br><br><strong>Step 1.1: Search www.tinkercad.com</strong><br><br>![image](image_6.png)</td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

44

<!-- SECTION: PAGE 46 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Alameda de Dranco University, Rojas Ave. Publication District, Dranco City, 8000 Dranco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Step 1.2: Create an Account and Log in to TinkerCAD

![image](image_5.png)

## Step 1.3: Navigate and Click “+ Create” and select 3D Design

## Step 2: Observe Your Workspace: You are now in the 3D editor. Let's identify the main parts of the screen.

![image](image_6.png)

### Step 2.1: TinkerCAD 3D Editor

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

45

<!-- SECTION: PAGE 47 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Díaz University, Rojas Ave. Publication District, Díaz City, 8000 Díaz, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

> **Workplane**: This is the big blue grid in the center. Think of it as your digital workbench where you will build everything.

> **Shapes Panel**: On the right side of the screen, you will see a panel with many basic shapes like boxes, cylinders, and spheres. This is your toolbox.

> **View Cube**: In the top-left corner, there is a cube that says "Top", "Front", etc. Clicking on any side of this cube will change your camera angle to look at your model from that direction.

## Step 3: Practice Moving Around: It's important to learn how to look at your model from all angles.

1. **To Orbit (look around)**: Hold down the right mouse button and move your mouse. You will see the workplane rotate.

2. **To Zoom**: Use the scroll wheel on your mouse to zoom in and out.

3. **To Pan (slide the view)**: Hold down the scroll wheel button (or Shift + right mouse button) and move your mouse to slide your view left, right, up, or down.

4. **Go Home**: If you ever get lost, just click the "Home View" button (it looks like a little house) on the left side, and it will reset your camera to the starting view.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

46

<!-- SECTION: PAGE 48 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Drooic University, Roos Ave, Publication District, Drooic City, 8000 Drooic, Jel Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Part B: Building the Keychain Base

### Step 4: Add a Box:
From the Shapes Panel on the right, find the red "Box" shape. Click on it, hold the mouse button down, and drag it to the center of the blue Workplane. Release the mouse button to place it.

![image](image_5.png)

### Step 4.1: Adding the box on the workplane

### Step 5: Resize the Box:
Click on the box you just placed. You will see small white and black squares, called "handles," appear on it.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

47

<!-- SECTION: PAGE 49 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Avenue de Drano University, Rios Ave. Publacion District, Drano City, 8000 Drano, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Step 5.1: Click on one of the white corner handles. You will see the length and width dimensions appear.

![image](image_5.png)

---

## Step 5.2: Change the length to 60 and the width to 20. You can do this by dragging the handle or by clicking on the number box and typing the value.

![image](image_6.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

48

<!-- SECTION: PAGE 50 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Aleneo de Draco University, Roaros Ave, Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Step 5.3: Now, click on the white handle on the top of the box. This controls the height. Change the height to 3. Your box should now be a flat rectangle.

### Part C: Adding a Hole for the Keyring

![image](image_5.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

49

<!-- SECTION: PAGE 51 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Rovira Ave. Publacion District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Step 6: Add a Cylinder:

From the Shapes Panel, find the "Cylinder" shape. It is usually gray and striped. Drag this cylinder anywhere onto the Workplane. This special cylinder is a "Hole".

![image](image_5.png)

## Step 7: Resize the Hole:

Click on the cylinder to select it. Using the white corner handles just like you did with the box, change its dimensions to be 5 by 5.

## Step 8: Position the Hole:

Click and drag the cylinder hole and move it to one end of your flat keychain base.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

50

<!-- SECTION: PAGE 52 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Roaros Ave, Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<div style="display: flex;">

<div style="width: 20%; background-color: #002868; height: 100%;"></div>

<div style="width: 80%; padding: 20px;">

![image](image_5.png)

**Step 9: Make sure it goes all the way through:** You might need to drag the black cone on top of the cylinder downwards to ensure it passes completely through the base from top to bottom.

---

**Part D: Adding Your Name**

**Step 10: Find the Text Tool:** In the Shapes Panel on the right, scroll down until you see the "Text" shape.

![image](image_6.png)

**Step 11: Add Text:** Click and drag "Text" shape onto your keychain base.

</div>

</div>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

51

<!-- SECTION: PAGE 53 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Aleneo de Drooic University, Roos Ave. Publacion District, Drooic City, 8000 Drooic del Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<div style="display: flex; align-items: center;">

<div style="width: 20%; background-color: #002868; height: 100%;"></div>

<div style="width: 80%; padding: 20px;">

![image](image_5.png)

**Step 12: Personalize the Text:** When the text shape is selected, a menu appears in the top-right. Find the field that says "Text" and replace the default word with your name or initials.

**Step 13: Resize and Position Your Name:**

![image](image_6.png)

**Step 13.1:** Use the corner handles to make the text smaller so it fits nicely on the keychain. *(Pro Tip: You can hold Shift + use the corner to resize the text for a more uniform size)*

</div>

</div>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

52

<!-- SECTION: PAGE 54 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Rojas Ave. Publacion District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<div style="display: flex;">

<div style="width: 20%; background-color: #002868; height: 100%;"></div>

<div style="width: 80%; padding: 20px;">

![image](image_5.png)

**Step 13.2:** Use the top white handle to change the height. A height of 4 usually looks good, as it will be slightly raised from the 3mm base.

![image](image_6.png)

**Step 13.3:** Click and drag your name to position it in the center of the keychain base.

</div>

</div>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

53

<!-- SECTION: PAGE 55 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Rojas Ave. Publacion District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Part E: Finishing and Exporting Your Model

### Step 14: Group the Shapes: This is the final and most important step to make your model one single object.

![image](image_5.png)

### Step 14.1: Click and hold your left mouse button on an empty part of the workplane.

### Step 14.2: Drag a red selection box over all of your objects (the base, the hole, and your text).

![image](image_6.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

54

<!-- SECTION: PAGE 56 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Aleneo de Draco University, Rojas Ave. Publacion District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Step 14.3: With everything selected, click the "Group" button in the toolbar at the top right. It looks like a square and a circle merging (Union Group).

![image](image_5.png)

## Step 14.4: You will see the hole get punched out, and the entire keychain will turn one solid color. It is now a single object.

## Step 15: Export for 3D Printing:

![image](image_6.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

55

<!-- SECTION: PAGE 57 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Step 15.1: Make sure your final keychain model is selected.  
*(Pro Tip: Hit CTRL + A for a faster selection of the entire model)*

<div style="text-align: center;">
  <button>Import</button>
  <button style="background-color: #e6f2ff; border: 1px solid #007acc;">Export</button>
  <button>Send To</button>
</div>

<div style="text-align: center; background-color: #2c3e50; color: white; padding: 10px; border-radius: 5px; font-size: 20px; font-weight: bold;">
  Download and 3D print
</div>

---

## Step 15.2: Click the "Export" button in the top-right corner.

<div style="text-align: center;">
  <div style="display: inline-block; background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;">
    <div style="display: flex; justify-content: space-between; font-size: 12px;">
      <span>Download</span>
      <span>3D Print</span>
      <span>×</span>
    </div>
    <div style="margin-top: 10px;">
      <label>Include</label>
      <input type="radio" name="include" id="everything" checked> <label for="everything">Everything in the design.</label><br>
      <input type="radio" name="include" id="selected" checked> <label for="selected">The selected shape.</label>
    </div>
    <div style="margin-top: 10px;">
      <div style="background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;">
        <div style="font-size: 12px;">Take Your Designs Further with Autodesk</div>
        <div style="display: flex; align-items: center; margin-top: 5px;">
          <span style="background-color: #ff6600; color: white; padding: 5px; font-weight: bold;">F</span>
          <span style="margin-left: 5px;">Autodesk Fusion</span>
          <span style="margin-left: auto;">&gt;</span>
        </div>
      </div>
      <div style="margin-top: 10px;">
        <div style="font-size: 12px;">For 3D Print</div>
        <div style="display: flex; gap: 10px; margin-top: 5px;">
          <input type="text" value=".OBJ" style="width: 80px;">
          <input type="text" value=".STL" style="width: 80px;">
        </div>
        <div style="margin-top: 5px;">
          <input type="text" value="GLTF (.glb)" style="width: 100%;">
        </div>
      </div>
      <div style="margin-top: 10px;">
        <div style="font-size: 12px;">For Lasercutting</div>
        <div style="display: flex; gap: 10px; margin-top: 5px;">
          <input type="text" value=".SVG" style="width: 80px;">
        </div>
      </div>
      <div style="margin-top: 10px; text-align: center;">
        <span style="font-size: 12px;">?</span> More information
      </div>
    </div>
  </div>
</div>

---

## Step 15.3: A menu will appear. Click on the ".STL" button.

<div style="background-color: #2c3e50; color: white; padding: 15px; border-radius: 5px; text-align: center;">
  <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
    ![image](image_5.png)
    <div>
      <strong>What do you want to do with Fantabulous Uusam.stl?</strong>
    </div>
  </div>
  <div style="margin-top: 10px;">
    <button>Open</button>
    <button>Save as</button>
    <button>Save</button>
  </div>
</div>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

56

<!-- SECTION: PAGE 58 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Droo University, Roes Ave, Publication District, Droo City, 8000 Droo, Jl Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td><strong>Step 15.4:</strong> Click Save. Your file will download. You have successfully designed and exported your first 3D model!</td>
  </tr>
  <tr>
    <td><strong>Advantages</strong></td>
    <td>
      <ul>
        <li><strong>Accessibility:</strong> TinkerCAD is a free, browser-based tool. It requires no installation, has very low system requirements, and automatically saves your work to the cloud.</li>
        <li><strong>Ease of Use:</strong> Its intuitive, drag-and-drop interface and simple controls make it the fastest and most straightforward way for a beginner to create a 3D printable model. The learning curve is practically non-existent.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><strong>Disadvantages</strong></td>
    <td>
      <ul>
        <li><strong>Limited Precision and Complexity:</strong> Its core advantage, simplicity, is also its main drawback. It lacks the advanced tools for creating complex curves, organic shapes, or dimension-driven parametric models required for professional engineering or artistic designs.</li>
        <li><strong>Dependence on Internet Connection:</strong> As a cloud-based application, it is unusable without a stable internet connection.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><strong>Synthesis</strong></td>
    <td>
      You have now completed the first and most creative step in the 3D printing journey: <strong>Digital Design.</strong><br><br>
      The TinkerCAD environment is designed to make modeling easy, but a successful print can only come from a well-constructed digital blueprint. Creating solid shapes ensures structural integrity, proper grouping combines parts into a single object, and a correct export generates a printable file.<br><br>
      Remember: “<em>A well-designed model is the blueprint for a successful print.</em>”
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

57

<!-- SECTION: PAGE 59 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Droo University, Roos Ave, Publication District, Droo City, 8000 Droo, Jl Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Reflection</th>
    <td>
      <p>Why is it important to start with a solid digital design before even thinking about the printer? If the digital model has design flaws, like parts that are not connected or walls that are too thin, what problems could happen during the printing stage?</p>
      <p>Through this activity, you learn that creation starts with a clear plan. Taking the time to properly design and assemble a digital model reflects foresight, creativity, and attention to detail, which are values essential in both engineering practice and personal growth.</p>
    </td>
  </tr>
  <tr>
    <th>FAQs</th>
    <td>
      <ol>
        <li><strong>How do I align objects perfectly?</strong>
          <ul>
            <li>Select the objects you want to align, then click the "Align" tool in the top-right toolbar. You will see nodes appear that allow you to align them to their centers or edges.</li>
          </ul>
        </li>
        <li><strong>My view is lost, or I am zoomed in too far. How do I fix it?</strong>
          <ul>
            <li>Click the "Home View" button (the house icon) to the left of the View Cube. This will reset the camera to its default position, showing all objects on your workplane.</li>
          </ul>
        </li>
        <li><strong>Can I measure distances?</strong>
          <ul>
            <li>Yes. Use the "Ruler" tool from the right-side panel. Place it on the workplane, and when you select an object, all dimensions and distances from the ruler's origin will be displayed.</li>
          </ul>
        </li>
        <li><strong>What is the difference between grouping a solid with a hole vs. two solids?</strong>
          <ul>
            <li>Grouping a solid and a "hole" subtracts the hole's shape from the solid. Grouping two solids combines them into a single, larger solid shape (a union operation).</li>
          </ul>
        </li>
      </ol>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

58

<!-- SECTION: PAGE 60 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave. Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## References

[1] Autodesk, “Tinkercad,” Autodesk. [Online]. Available: https://www.tinkercad.com.

[2] “STL (file format),” Wikipedia, Oct. 15, 2025. [Online]. Available: https://en.wikipedia.org/wiki/STL_(file_format).

[3] E. Milková and A. Šimková, “Using and Citation of 3D Modeling Software for 3D Printers,” NAUN, 2017.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

59

<!-- SECTION: PAGE 61 -->

Local Engine Failed: HTTPConnectionPool(host='192.168.1.91', port=8000): Read timed out. (read timeout=120)


<!-- SECTION: PAGE 62 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Droo University, Roes Ave, Publication District, Droo City, 8000 Droo, Jel Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Course Title</th>
    <td>Basic Additive Manufacturing Laboratory Manual (3D Printing)</td>
  </tr>
  <tr>
    <th>Lesson No. and Title</th>
    <td>Laboratory 02: Toolpath Logic - Translating Models into Layers</td>
  </tr>
  <tr>
    <th>Learning Outcomes</th>
    <td>
      1. Understand the function of slicing software in the 3D printing workflow.<br>
      2. Successfully import a 3D model (STL file) into Creality Slicer and navigate the basic user interface.<br>
      3. Apply fundamental slicing settings, generate the print path (G-code), and export the file for printing.
    </td>
  </tr>
  <tr>
    <th>Time Frame</th>
    <td>This laboratory activity can be finished in 30 MINUTES.</td>
  </tr>
  <tr>
    <th>Introduction</th>
    <td>
      ![image](image_5.png) ![image](image_6.png) ![image](image_7.png)<br>
      <strong>Figure 1: 3D Slicing Softwares</strong><br><br>
      A 3D model is a digital blueprint. To turn that blueprint into a physical object, it must be translated into a language the 3D printer can understand. This translation process is called "slicing." Slicing software cuts the 3D model into hundreds or thousands of thin horizontal layers and generates a file with coordinate instructions—known as G-code—that tells the printer exactly where to move and when to deposit material for each layer.<br><br>
      ![image](image_8.png)<br>
      <strong>Figure 1.1: Creality Print Slicer</strong>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_9.png) ![image](image_10.png) ![image](image_11.png) ![image](image_12.png)

---

61

<!-- SECTION: PAGE 63 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Drooia University, Roaros Ave, Publication District, Drooia City, 8000 Drooia, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td rowspan="2" style="background-color: #002060; color: white; padding: 10px; vertical-align: top;">
      <strong>Lesson</strong>
    </td>
    <td>
      Different printer manufacturers often provide their own optimized slicers, such as <strong>Eiger for Markforged printers</strong>, <strong>Bambu Studio for Bambu Lab</strong>, or <strong>FlashPrint for Flashforge</strong>. For this activity, we will use Creality Slicer, as it is specifically configured for the Creality Ender 3 V3 KE printer, ensuring a straightforward and reliable workflow.
    </td>
  </tr>
  <tr>
    <td>
      <strong>Part A: Downloading and Installing Creality Slicer</strong>

      ![image](image_5.png)

      <strong>Step 1: Find the Software:</strong> Open a web browser and search for "Creality Slicer download".

      ![image](image_6.png)

      <strong>Step2: Navigate to the Official Website:</strong> Click on the link that leads to the official Creality software download page. It is important to download
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

62

<!-- SECTION: PAGE 64 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Drooic University, Roos Ave. Publication District, Drooic City, 8000 Drooic, Jel Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

directly from the manufacturer to ensure you have the latest and safest version.

**Step 3: Download the Installer:** On the download page, find the latest version of Creality Slicer. Select the correct version for your computer's operating system (e.g., Windows or macOS) and download the installer file.

**Step 4: Install the Application:** Once the download is complete, locate the installer file in your "Downloads" folder and run it. Follow the on-screen prompts to complete the installation. You can accept the default settings.

## Part B: First-Time Setup and Interface

![image](image_5.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

63

<!-- SECTION: PAGE 65 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Avenue de Drano University, Rovira Ave, Publication District, Drano City, 8000 Drano, Jol Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Step 5: Open Creality Slicer: Launch the application you just installed.

## Step 6: Printer Configuration:

![image](image_5.png)

*Please select your login area*

- Asia-Pacific
- Chinese Mainland
- Europe
- North America
- Others

---

## Step 6.1: The first time you open the software you will be prompted to select your log in area select “Asia-Pacific”

![image](image_6.png)

*Welcome to Creality Print*

- Add printers and manage print jobs from the cloud

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

64

<!-- SECTION: PAGE 66 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Aleneo de Draco University, Raros Ave. Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Step 6.2: Select “Skip Printer Connection For Now”

![image](image_5.png)

- **Search Results**
  - Creality Ender-3 V3 KE
    - 220°220°240
    - Diameter: 0.4mm
- **Confirm** | **Cancel**

---

## Step 6.3: This is a crucial step, you will be prompted to select a list of 3D printers you own. Search and Select “Creality Ender-3 V3 KE” and Confirm.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

65

<!-- SECTION: PAGE 67 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Avenue de Drano University, Rovira Ave. Publacion District, Drano City, 8000 Drano, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

![image](image_5.png)

**Step 6.4:** You will be directed to its main page of the slicer.

**Step 7:** Familiarize with the Workspace: Take a moment to look at the main screen.

![image](image_6.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

66

<!-- SECTION: PAGE 68 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Rojas Ave. Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

> **Build Plate**: The large grid area in the center is a virtual representation of the printer's physical build surface.

![image](image_5.png)

> **File/Import Icon**: Look for a folder icon in the top-left corner. This is what you will use to open your 3D model.

![image](image_6.png)

> **Manipulation Tools**: A toolbar on the left side of the screen contains tools to Move, Scale, and Rotate your model on the build plate.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

67

<!-- SECTION: PAGE 69 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Avenue de Drano University, Roanoke Ave. Publication District, Drano City, 8000 Drano, Del Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Print Settings Panel:

The panel on the right is where you will control the slicing parameters. This is the most important area for preparing a print.

---

## Part C: Importing and Preparing the Model

![image](image_5.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

68

<!-- SECTION: PAGE 70 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Avenue de Draco University, Roca Ave, Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Step 8: Import Your Keychain STL

Click the "Import" or folder icon. Find and select the keychain ".STL" file you saved from TinkerCAD in the previous lab. The model will now appear on the virtual build plate.

![image](image_5.png)

## Step 9: Check Model Orientation

The keychain should automatically load lying flat on its back. This is the best orientation for printing it. If your model were to load standing on its edge, you would need to use the Rotate tool to lay it down flat. A flat base ensures the print sticks well to the build plate.

## Part D: Applying Slicing Settings

For a beginner-friendly print, we will use the excellent default profiles provided.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

69

<!-- SECTION: PAGE 71 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Avenue de Drano University, Rovira Ave, Publication District, Drano City, 8000 Drano, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

![image](image_5.png)

**Step 10: Select Print Profile:** In the Print Settings panel on the right, find the "Profile" dropdown menu. Click it and select the "Standard Quality - 0.2mm" profile. This profile offers a great balance between print speed and visual detail.

<table>
  <tr>
    <th>Infill</th>
    <th></th>
  </tr>
  <tr>
    <td>Sparse infill density</td>
    <td>15 %</td>
  </tr>
  <tr>
    <td>Sparse infill pattern</td>
    <td>Rectilinear</td>
  </tr>
  <tr>
    <td>Internal solid infill pattern</td>
    <td>Monotonic</td>
  </tr>
  <tr>
    <td>Anchor solid infill by X mm</td>
    <td>0 mm or %</td>
  </tr>
</table>

**Step 11: Check Infill Setting:** Look for the "Infill" setting. It should default to a value around 15%. This means the inside of your keychain won't be solid plastic but will be filled with a sturdy, grid-like pattern that is 15% dense. This saves a lot of time and material.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

70

<!-- SECTION: PAGE 72 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Aleneo de Draco University, Rodeo Ave, Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Support Settings

<table>
  <tr>
    <td>Enable support</td>
    <td><input type="checkbox" /></td>
  </tr>
  <tr>
    <td>Type</td>
    <td><select><option>Normal(auto)</option></select></td>
  </tr>
  <tr>
    <td>Style</td>
    <td><select><option>Default</option></select></td>
  </tr>
  <tr>
    <td>Threshold angle</td>
    <td><input type="range" value="30" /></td>
  </tr>
  <tr>
    <td>On build plate only</td>
    <td><input type="checkbox" /></td>
  </tr>
  <tr>
    <td colspan="2"><strong>Filament for Supports</strong></td>
  </tr>
  <tr>
    <td>Support/raft base</td>
    <td><select><option>Default</option></select></td>
  </tr>
  <tr>
    <td>Support/raft interface</td>
    <td><select><option>Default</option></select></td>
  </tr>
</table>

---

### Step 12: Check Support Setting

Find the "Support" setting section. Make sure the "Generate Support" checkbox is not ticked. Our simple keychain model is flat and has no features that would need extra support structures to be printed successfully.

---

## Part E: Slicing and Exporting the Final File

![image](image_5.png)

**Slice plate**  
**Send print**

---

### Step 13: Slice the Model

Now that the settings are confirmed, click the green "Slice" button, located at the bottom-right of the screen. The software will calculate all the printer's movements needed to build the model.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

71

<!-- SECTION: PAGE 73 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Aleneo de Draco University, Rojas Ave. Publacion District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

![image](image_5.png)

**Step 14: Preview the Toolpath:** After a few moments, the view will switch to a "Preview" mode. This is a simulation of the printing process. You can use the vertical slider on the right side to scrub through each individual layer, from the bottom to the top. This view also gives you an estimated print time and the amount of material that will be used.

![image](image_6.png)

**Step 15: Export the G-Code File:** Finally, click the "Save to Disk" (or "Save to Removable Drive") button. A save window will pop up. This is where you save the final instruction file, which will have a .gcode file extension. Save this file directly to the USB drive or SD card you will plug into the 3D printer.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

72

<!-- SECTION: PAGE 74 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Alameda de Driano University, Rojas Ave. Publication District, Driano City, 8000 Driano, Jal. Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td><strong>Congratulations!</strong> You have now successfully converted a 3D model into a printable G-code file.</td>
  </tr>
  <tr>
    <td><strong>Advantages</strong></td>
    <td>
      <ul>
        <li><strong>Optimized Profiles:</strong> Creality Slicer is pre-loaded with fine-tuned settings for Creality printers like the Ender 3 V3 KE, which greatly increases the chance of a successful print without needing complex adjustments.</li>
        <li><strong>Simple Interface:</strong> The layout is clean and focuses on the most essential settings, making it less intimidating and easier for a beginner to navigate than more advanced, feature-packed slicers.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><strong>Disadvantages</strong></td>
    <td>
      <ul>
        <li><strong>Limited Advanced Control:</strong> It lacks some of the highly granular settings and experimental features (like custom toolpath scripting or tree supports) that are available in other slicers like <em>Ultimaker Cura</em> or <em>PrusaSlicer</em>.</li>
        <li><strong>Potentially Slower Updates:</strong> As proprietary software, it may not be updated with the newest slicing features as frequently as its open-source counterparts.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><strong>Synthesis</strong></td>
    <td>
      You have now mastered the crucial translation step in 3D printing: <strong>Slicing</strong>.
      <br><br>
      Creality Slicer is designed to optimize the printing process, but it can only perform well if the settings are properly chosen. Applying the correct profile ensures quality, setting the right infill provides strength, and previewing the toolpath prevents errors.
      <br><br>
      Remember: “<em>A well-sliced file is the instruction manual for a perfect print.</em>”
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

73

<!-- SECTION: PAGE 75 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Droo University, Roos Ave, Publication District, Droo City, 8000 Droo, Jl Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Reflection</th>
    <td>Why is the slicing stage so critical in the 3D printing workflow? If the slicing settings are chosen poorly, such as having zero infill for a structural part or incorrect support settings for a model with overhangs, what possible printing problems might occur?<br><br>Through this activity, you learn that a good plan requires clear instructions. Taking the time to properly slice a model reflects strategic thinking, precision, and an understanding of the process, which are values essential in both engineering practice and personal growth.</td>
  </tr>
  <tr>
    <th>FAQ</th>
    <td>
      <ol>
        <li><strong>What is the difference between an STL file and a G-code file?</strong>
          <ul>
            <li>An STL file is a 3D model; it describes the shape and geometry of your object. A G-code file is a set of specific, layer-by-layer instructions that tells the 3D printer's hardware how to move to create that shape. You cannot print an STL directly.</li>
          </ul>
        </li>
        <li><strong>What is "infill" and why is it important?</strong>
          <ul>
            <li>Infill is the internal structure printed inside a model. A model is rarely printed 100% solid. Infill (e.g., 15% grid) provides internal support to the top surfaces and gives the object strength without using excessive material or taking a long time to print.</li>
          </ul>
        </li>
        <li><strong>What are "supports" and when do I need them?</strong>
          <ul>
            <li>A 3D printer builds layer by layer from the bottom up. It cannot print in mid-air. Supports are disposable scaffolding structures the slicer automatically adds to hold up parts of a model that have steep overhangs (typically over 45-50 degrees) or bridges.</li>
          </ul>
        </li>
        <li><strong>How can I reduce the estimated print time?</strong>
          <ul>
            <li>The easiest ways to reduce print time are by increasing the layer height (e.g., from 0.2mm to 0.28mm, which creates a lower-quality print), reducing the infill percentage, or scaling the model down in size.</li>
          </ul>
        </li>
      </ol>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

74

<!-- SECTION: PAGE 76 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Drooic University, Roesse Ave, Publication District, Drooic City, 8000 Drooic, Jel Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## References

[1] Creality, “Creality Slicer User Manual - EN 4.8.0,” Scribd. [Online]. Available:  
https://www.scribd.com/document/566842607/Creality-Slicer-User-Manual-EN-4-8-0.

[2] Sinterit, “What is 3D slicing in printing? Key to print quality and success,” Sinterit. [Online]. Available:  
https://www.sinterit.com/what-is-3d-slicing-in-printing/.

[3] 3Dnatives, “What is a G-Code and What is its Use in 3D Printing?,” 3Dnatives, Sep. 23, 2021. [Online]. Available:  
https://www.3dnatives.com/en/g-code-in-3d-printing-230920214/

[4] All3DP, “The Main 3D Printing File Formats,” All3DP. [Online]. Available:  
https://all3dp.com/2/3d-printer-file-format-3d-printing-file-format/.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

75

<!-- SECTION: PAGE 77 -->

Local Engine Failed: HTTPConnectionPool(host='192.168.1.91', port=8000): Read timed out. (read timeout=120)


<!-- SECTION: PAGE 78 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Alameda de Driano University, Rojas Ave. Publication District, Driano City, 8000 Driano, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Course Title</th>
    <td>Basic Additive Manufacturing Laboratory Manual (3D Printing)</td>
  </tr>
  <tr>
    <th>Lesson No. and Title</th>
    <td>Laboratory 03: Machine Readiness: Calibration and First Runs</td>
  </tr>
  <tr>
    <th>Learning Outcomes</th>
    <td>
      1. Assemble the Creality Ender 3 V3 SE 3D printer.<br>
      2. Perform printer initial setup and calibration.<br>
      3. Familiarize themselves with the proper before-print practices in 3D printing.
    </td>
  </tr>
  <tr>
    <th>Time Frame</th>
    <td>This laboratory activity can be finished in 1 HOUR.</td>
  </tr>
  <tr>
    <th>Introduction</th>
    <td>
      Hello learners!<br><br>
      Welcome to your first hands-on machine readiness lab. Today, you will assemble and prepare your very own Creality Ender 3 V3 SE printer — the tool that will turn your digital designs into real, physical objects.<br><br>
      Before we start printing, we need to make sure the printer is correctly set up, calibrated, and tested. Think of this as “warming up” your machine before a marathon. If your printer is not properly assembled or leveled, your prints will fail, no matter how perfect your model is.<br><br>
      By the end of this lab, your printer will be fully ready for its first successful print.
    </td>
  </tr>
  <tr>
    <th>Laboratory</th>
    <td>
      <strong>Printer Assembly</strong><br><br>
      For the following steps, kindly refer to the Creality Ender 3 V3 SE Manual that is part of your kit. This can also be accessed through the QR Code.<br>
      <em>(Note: If already done with Assembly, please proceed to Initial Setup and Calibration)</em>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

77

<!-- SECTION: PAGE 79 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Díaz University, Rojas Ave. Publication District, Díaz City, 8000 Díaz, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

Before calibration, let us build the foundation. The assembly process involves attaching the major components together. Steps to assemble (Manual Pages 3–9):

1. **Install the Gantry Frame:**
   - Place the gantry frame on the base and align the screw holes.
   - Use M3x14 screws from the bottom and M3x8 screws from the rear to secure it firmly.

2. **Attach the Display Screen:**
   - Mount the screen on the right side of the base using M4x10 screws.
   - Connect the display cable securely to the port behind the screen.

3. **Install the Filament Rack:**
   - Mount the rack to the top of the gantry frame using M5x8 screws.

4. **Connect the Cables and Motors:**
   - Connect the X-axis motor, Z-axis motor, and extruder cable according to the wiring diagram on Manual Page 6.
   - Make sure cables are not twisted or folded.

5. **Power Connection:**
   - Set the correct voltage (230V for 220–240V outlets or 115V for 100–120V).
   - Use only the provided power cable.

**Safety Tip:** Never power on the printer until all components are secured. Loose wiring can cause the printer to short or stop mid-print.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

78

<!-- SECTION: PAGE 80 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave. Publacion District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Initial Setup and Calibration

Now that your printer is fully assembled, it is time to make it ready for printing. This process is called **initial setup and calibration**, where you make sure every moving part, sensor, and filament system is properly aligned and functioning before you begin printing.

Please refer to the *Creality Ender 3 V3 SE Manual, Pages 7–16* for step-by-step visuals and details of each procedure below.

### Step 1: Power On and Verify Connections

Before anything else, check that the power cable is connected properly.

- Set the voltage selector at the rear to the correct setting for your region (115V or 230V).
- Switch the printer on and wait for the screen to light up.
- Ø If the display or motors do not respond, review **Manual Page 21 (Circuit Wiring)** to ensure all plugs are properly inserted.

**Why this matters:** A proper electrical check prevents startup issues or damage caused by loose or misconnected wires.

### Step 2: Bed Leveling

- From the main screen, select “Leveling.”
- The printer will automatically move the printhead and probe multiple points on the bed using the built-in CR-Touch sensor.
- Wait for the full leveling process to finish.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

79

<!-- SECTION: PAGE 81 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Droo University, Roes Ave, Publication District, Droo City, 8000 Droo, Jl Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

> You can observe the sensor touch different points to detect bed height variation. Once done, the printer will store the leveling data automatically.

**Manual Reference:** Page 10 – 4.1 Leveling

**Why this matters:** Accurate bed leveling ensures the first layer of your print adheres well to the bed. Uneven leveling often causes peeling or warping.

## Step 3: Preheat the Printer

> Before loading filament, preheat the printer according to your material type.

> From the menu, select “Prepare” → “Preheat PLA.” This will heat the nozzle and the bed automatically to the recommended PLA settings:

- Nozzle temperature: 205°C
- Bed temperature: 60°C

**Manual Reference:** Page 11 – 4.2 Printer Preheating

**Why this matters:** Preheating softens the filament for smooth feeding and prevents nozzle blockage during loading.

## 4: Load the Filament

> Cut the filament tip at a 45-degree angle for smoother feeding.

> Insert it into the extruder inlet and push gently until resistance is felt.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

80

<!-- SECTION: PAGE 82 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

> ➤ Use the “Auto Feed” or “Load Filament” option on the display to help guide it to the nozzle.  
> ➤ Wait until molten filament begins to extrude evenly.

**Manual Reference:** Pages 7–9 – 3.5 Filament Loading

**Why this matters:** Proper filament loading prevents under-extrusion and ensures consistent flow during printing.

## Quick Summary of Setup Sequence

<table>
  <thead>
    <tr>
      <th>Step</th>
      <th>Procedure</th>
      <th>Manual Reference</th>
      <th>Key Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Power On & Wiring Check</td>
      <td>p. 21</td>
      <td>Confirm safe connections</td>
    </tr>
    <tr>
      <td>2</td>
      <td>Bed Leveling</td>
      <td>p. 10</td>
      <td>Ensure surface flatness</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Preheat Printer</td>
      <td>p. 11</td>
      <td>Prepare for filament loading</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Load Filament</td>
      <td>pp. 7–9</td>
      <td>Feed filament correctly</td>
    </tr>
    <tr>
      <td>5</td>
      <td>Slice Model</td>
      <td>pp. 12–13</td>
      <td>Convert design into G-code</td>
    </tr>
    <tr>
      <td>6</td>
      <td>Start Print</td>
      <td>pp. 14–16</td>
      <td>Begin printing test file</td>
    </tr>
    <tr>
      <td>7</td>
      <td>Observe First Layer</td>
      <td>p. 15</td>
      <td>Verify adhesion and flow</td>
    </tr>
    <tr>
      <td>8</td>
      <td>Cool Down</td>
      <td>p. 16</td>
      <td>Safely end print session</td>
    </tr>
  </tbody>
</table>

## Before Print Practices

Every 3D printing session should begin with a short checklist:

1. **Clean the Bed** – Wipe the surface to remove dust and residue.
2. **Check Filament Condition** – Make sure it is dry, untangled, and loaded correctly.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

81

<!-- SECTION: PAGE 83 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Droo University, Roar Ave, Publication District, Droo City, 8000 Droo, Jai Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td rowspan="2" style="background-color: #002855; color: white; padding: 10px; vertical-align: top; width: 20%;">&nbsp;</td>
    <td style="padding: 10px; vertical-align: top;">
      3. <strong>Recheck Leveling</strong> – Small shifts can happen after transport or previous prints.<br>
      4. <strong>Confirm Temperature Settings</strong> – Match the settings to your filament type.<br>
      5. <strong>Inspect the Nozzle and Bed</strong> – Ensure there is no leftover filament stuck.<br>
      6. <strong>Load Correct G-code</strong> – File name should be short and in English (Manual Page 14).<br><br>
      These simple steps prevent common beginner mistakes like poor adhesion, under-extrusion, and nozzle blockage.
    </td>
  </tr>
  <tr>
    <td style="padding: 10px; vertical-align: top;">
      <strong>Synthesis</strong><br><br>
      You have now completed the three most important steps for any 3D printer setup: <strong>Assembly, Calibration, and Readiness</strong>.<br><br>
      The Creality Ender 3 V3 SE is designed to make printing easy, but it can only perform well if the machine is properly tuned. Calibration ensures accuracy, preheating prevents clogs, and clean practices maintain print quality.<br><br>
      Remember: “A well-prepared machine makes a perfect print.”
    </td>
  </tr>
  <tr>
    <td style="background-color: #002855; color: white; padding: 10px; vertical-align: top; width: 20%;">&nbsp;</td>
    <td style="padding: 10px; vertical-align: top;">
      <strong>Reflection</strong><br><br>
      Why is machine calibration important before the first print? If the nozzle and bed are not properly aligned, what possible printing problems might occur?<br><br>
      Through this activity, you learn that <strong>precision starts with preparation</strong>. Taking time to calibrate the machine reflects excellence, care, and accountability, which are values essential in both engineering practice and personal growth.
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

82

<!-- SECTION: PAGE 84 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Alameda de Dania University, Roanoke Ave. Publication District, Dania City, 8000 Dania, Jal. Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## FAQs

1. **How often should I level the bed?**
   - You should level the bed before your first print and recheck it weekly or whenever prints do not stick well.

2. **Why is the first layer important?**
   - The first layer determines if the entire model will stick to the bed. Poor adhesion in the first layer often leads to failed prints.

3. **What should I do if the filament is not extruding?**
   - Preheat the nozzle, unload the filament, trim the tip, and reload it. If it still fails, check for a clogged nozzle.

4. **What temperature should I use for PLA?**
   - Use a nozzle temperature of $205^\circ C$ and a bed temperature of $60^\circ C$ (Page 11).

5. **Why is my print not sticking to the bed?**
   - The bed may not be level or may be dirty. Re-level it, clean the surface, and check your Z-offset setting.

6. **What should I do if I hear grinding or clicking noises?**
   - That usually means the extruder motor is skipping. Check for filament jams or blocked pathways.

7. **Can I print flexible materials like TPU?**
   - Yes, but slow down the print speed to around $40 \, \text{mm/s}$ and make sure your filament path is straight (Page 11).

8. **How do I prevent warping or corners lifting?**
   - Preheat the bed, enable cooling fans, and use a brim or glue stick for better adhesion.

9. **How do I clean the nozzle safely?**
   - Heat the nozzle first, then use a nozzle cleaning needle while wearing protective gloves (Page 18).

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

83

<!-- SECTION: PAGE 85 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Drooic University, Roes Ave, Publication District, Drooic City, 8000 Drooic, Jel Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td>
      <strong>10. What should I check before every print?</strong>
      <ul>
        <li>Confirm the bed is level, filament is loaded, temperatures are correct, and there are no leftover materials on the bed or nozzle.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><strong>References</strong></td>
    <td>
      Creality 3D. *Ender 3 V3 SE User Manual*, Version 1.0, Shenzhen Creality 3D Technology Co., Ltd., 2023.
      <ul>
        <li>Assembly Procedure: Pages 3–9</li>
        <li>Filament Loading: Pages 7–9</li>
        <li>Bed Leveling: Page 10</li>
        <li>Preheat and Material Setup: Page 11</li>
        <li>Slicing and Printing: Pages 12–16</li>
        <li>Maintenance and Troubleshooting: Pages 17–19</li>
      </ul>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

84

<!-- SECTION: PAGE 86 -->

Local Engine Failed: HTTPConnectionPool(host='192.168.1.91', port=8000): Read timed out. (read timeout=120)


<!-- SECTION: PAGE 87 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Droo University, Roos Ave, Publication District, Droo City, 8000 Droo, Jl Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Course Title</th>
    <td>Basic Additive Manufacturing Laboratory Manual (3D Printing)</td>
  </tr>
  <tr>
    <th>Lesson No. and Title</th>
    <td>Laboratory 04: Performance Metrics: Evaluating First Prints</td>
  </tr>
  <tr>
    <th>Learning Outcomes</th>
    <td>
      1. Understand the basics of printing calibration.<br>
      2. Identify possible issues that occur during the 3D printing process.<br>
      3. Apply appropriate solutions to common print defects using data from the calibration cube.
    </td>
  </tr>
  <tr>
    <th>Time Frame</th>
    <td>This laboratory activity can be finished in 1 HOUR.</td>
  </tr>
  <tr>
    <th>Introduction</th>
    <td>
      In the last laboratory, you assembled and calibrated your 3D printer. Today, you will take the next step, testing performance using a simple but powerful tool: the 20 mm XYZ Calibration Cube.<br><br>
      This cube helps you evaluate your printer’s accuracy, motion consistency, and extrusion quality. Every side of the cube reveals something about your printer’s health, the X, Y, and Z letters correspond to the three axes of motion.<br><br>
      By analyzing this cube, you will learn how to read the signs of a well-tuned printer and how to correct common issues like over-extrusion, layer shifting, or dimension inaccuracy.
    </td>
  </tr>
  <tr>
    <th>Laboratory</th>
    <td>
      <strong>1. Print Instructions for the XYZ Calibration Cube</strong><br><br>
      <strong>Prepare the G-code file</strong><br><br>
      1. Download or import the 20 mm XYZ Calibration Cube.stl model into the Creality Print.
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

86

<!-- SECTION: PAGE 88 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave. Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## 2. Set the following recommended system print parameters for PLA:

![image](image_5.png)

- **Filament**
  - 1
  - CR-PLA ▼

- **Process**
  - Global Objects

- **Nozzle**
  - 0.20mm Standard @Creality Ender-3 V3 KE 0.4 nozzle

---

## 3. Click Slice and save the G-code to your SD card.

*For screen navigation, refer to Creality Ender 3 V3 SE Manual Pages 14–16 (Printing Files).*

---

## 2. Expected Output

After a successful print, you should obtain:

- A 20 mm cube with clear X, Y, and Z letters embossed on each side.
- Flat and smooth bottom surface with no warping.
- Layer lines that are even and tightly bonded.
- Actual dimensions close to $20.00 \text{ mm} \pm 0.2 \text{ mm}$ in all axes.

You can verify this by measuring with a digital caliper and comparing:

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

87

<!-- SECTION: PAGE 89 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Droo University, Roes Ave. Publication District, Droo City, 8000 Droo, Jl Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <thead>
    <tr>
      <th>Axis</th>
      <th>Target (mm)</th>
      <th>Acceptable Range (mm)</th>
      <th>Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>X</td>
      <td>20.00</td>
      <td>19.80 – 20.20</td>
      <td>Left–Right movement</td>
    </tr>
    <tr>
      <td>Y</td>
      <td>20.00</td>
      <td>19.80 – 20.20</td>
      <td>Front–Back movement</td>
    </tr>
    <tr>
      <td>Z</td>
      <td>20.00</td>
      <td>19.80 – 20.20</td>
      <td>Up–Down movement</td>
    </tr>
  </tbody>
</table>

**What this tells you:** If all three axes are close to 20 mm and surfaces are clean, your printer is well-calibrated.

![image](image_5.png)

*A sample of a perfect XYZ Calibration Cube*

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

88

<!-- SECTION: PAGE 90 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Alameda de Drago University, Rojas Ave. Publication District, Drago City, 8000 Drago, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## 3. Possible Print Issues and Their Solutions

<table>
  <thead>
    <tr>
      <th>Problem</th>
      <th>Description</th>
      <th>Likely Cause</th>
      <th>Solution</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Dimensional error (cube not 20 mm)</td>
      <td>Cube measures smaller or larger than 20 mm</td>
      <td>Incorrect step/mm calibration in firmware or slicer</td>
      <td>Re-calibrate X/Y/Z steps; verify belt tension; adjust in slicer flow compensation.</td>
    </tr>
    <tr>
      <td>Over-extrusion (bulging edges or blobs)</td>
      <td>Extra plastic makes surfaces rough or letters unreadable</td>
      <td>Flow rate too high or nozzle temp too hot</td>
      <td>Reduce flow to 95–98 %; lower nozzle temp by 5 °C</td>
    </tr>
    <tr>
      <td>Under-extrusion (gaps between lines)</td>
      <td>Missing lines or weak walls</td>
      <td>Clogged nozzle or low flow</td>
      <td>Clean nozzle; check filament path; increase extrusion multiplier slightly</td>
    </tr>
    <tr>
      <td>Layer shifting</td>
      <td>Layers not aligned; cube walls stagger</td>
      <td>Loose belt, pulley, or motor skip</td>
      <td>Tighten belts and pulley screws; reduce print speed to 40 mm/s</td>
    </tr>
    <tr>
      <td>Z-banding or rippling</td>
      <td>Visible vertical waves</td>
      <td>Bent Z-rod or unstable bed</td>
      <td>Lubricate or straighten lead screw; verify bed is secure</td>
    </tr>
    <tr>
      <td>Warping or corners lifting</td>
      <td>Corners rise off bed</td>
      <td>Bed not hot enough or dirty surface</td>
      <td>Re-clean bed; apply glue stick; ensure bed temp = 60 °C</td>
    </tr>
    <tr>
      <td>Stringing between letters</td>
      <td>Thin hairs of plastic between X/Y/Z</td>
      <td>Retraction too low</td>
      <td>Increase retraction distance or speed in slicer</td>
    </tr>
    <tr>
      <td>Poor first layer</td>
      <td>Uneven, rough, or peeling bottom</td>
      <td>Bed not leveled or nozzle too far</td>
      <td>Re-level bed; adjust Z-offset to 0.1 mm</td>
    </tr>
    <tr>
      <td>Nozzle clog during print</td>
      <td>Extrusion stops mid-print</td>
      <td>Dust or burnt residue in nozzle</td>
      <td>Perform hot-end cleaning or cold-pull method</td>
    </tr>
    <tr>
      <td>Inconsistent dimensions in repeated prints</td>
      <td>Results vary each time</td>
      <td>Mechanical looseness</td>
      <td>Check frame screws, belts, and V-wheels for play (Loose feels)</td>
    </tr>
  </tbody>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

89

<!-- SECTION: PAGE 91 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Rodeo Ave. Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<div style="display: flex;">

<div style="width: 20%; background-color: #002868; height: 100%;"></div>

<div style="width: 80%; padding: 20px;">

![image](image_5.png)

**Over-Extrusion.** These are the different cases of overextrusion. A common feature in over-extruded print is the visible layer of plastic residue.

![image](image_6.png)

**Under-Extrusion.** The indicator for this issue is the “holes” that can be found on the top layer, as well as the first layer print. It is important to

</div>

</div>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

90

<!-- SECTION: PAGE 92 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave. Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

monitor the first layer to avoid several print issues, including under-extrusion.

![image](image_5.png)

**Layer Shifting.** The indicator for this issue is the sudden shift in layers observable in the Z axis. This happens due to several factors, one is the bed plate temperature is not hot enough for the material to adhere.

![image](image_6.png)

**Z Banding.** Happens when there is vibration on the printer gantry. This vibration causes the layers to move slightly making the visible Z layer bands.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

91

<!-- SECTION: PAGE 93 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td>
      ![image](image_5.png)
      <p><strong>Stringing.</strong> In this image, visible stringing can be observed on the spot of a small hanging area. In normal printing conditions, this must not happen on small overhangs.</p>
    </td>
  </tr>
  <tr>
    <td><strong>Synthesis</strong></td>
    <td>
      The <strong>XYZ Calibration Cube</strong> is a simple yet powerful diagnostic model. It helps you visualize how mechanical, thermal, and extrusion factors affect print accuracy. A small measurement error can reveal belt looseness, motor calibration, or even filament flow problems.
      <br><br>
      Always remember: “Calibrate, test, adjust, and print again.” The more you practice, the more predictable your prints become.
    </td>
  </tr>
  <tr>
    <td><strong>Reflection</strong></td>
    <td>
      After printing your XYZ calibration cube, which axis (X, Y, or Z) showed the largest deviation from 20 mm? What adjustment would you perform to improve accuracy on that axis? The XYZ Calibration Cube teaches the value of precision and consistency. Even a small deviation shows how minor mechanical or calibration issues can affect the final output.
    </td>
  </tr>
  <tr>
    <td><strong>FAQs</strong></td>
    <td>
      1. Why do we use a calibration cube instead of another model?
      <ul>
        <li>Because its simple geometry lets you measure motion accuracy easily along all three axes.</li>
      </ul>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

92

<!-- SECTION: PAGE 94 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Alameda de Dania University, Rodeo Ave. Publication District, Dania City, 8000 Dania, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## 2. What measuring tool should I use for checking the cube?

- A *digital caliper* gives the most accurate readings for 3D print calibration.

## 3. How often should I print a calibration cube?

- Print one whenever you change filament type, nozzle, or after major maintenance.

## 4. My cube is undersized on all sides. What should I check?

- Check your *steps/mm* settings or reduce *flow rate*; belts may also be too tight.

## 5. What does rough or uneven lettering mean?

- It usually means *over-extrusion* or the *nozzle temperature* is too high. Lower temperature by 5 °C and clean the nozzle.

## 6. Why do my layers shift halfway through the cube?

- Your belts or pulleys are likely loose, or the print speed is too fast. Tighten and slow down to 40 mm/s.

## 7. Why are there gaps between layers?

- The filament might not be feeding smoothly; check spool tension and extruder gears.

## 8. How can I get more accurate cube measurements?

- Calibrate your *E-steps* and make sure the bed is square to the Z-axis.

## 9. Should I re-level the bed before every test print?

- Yes. Small movements during previous prints can alter bed alignment.

## 10. What if the cube sticks too hard to the bed?

- Allow it to cool before removal or use a *flexible build plate* to release the print safely.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

93

<!-- SECTION: PAGE 95 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Alameda de Dania University, Rodeo Ave. Publication District, Dania City, 8000 Dania, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## References

Creality 3D. *Ender-3 V3 SE User Manual*, Version 1.0, Shenzhen Creality 3D Technology Co., Ltd., 2023.

- Filament Loading: pp. 7–9
- Leveling: p. 10
- Preheating: p. 11
- Printing Files: pp. 14–16
- Maintenance and Troubleshooting: pp. 17–19

### Online Visual References (Calibration Cube Examples):

- Reddit. (n.d.). *XYZ Calibration Cube with Top Layer Overfill*.  
  https://preview.redd.it/om5gn9rd90j81.jpg

- Reddit. (n.d.). *Extra Plastic on Top Surface of Calibration Cube*.  
  https://preview.redd.it/the-tops-of-my-xyz-calibration-test-cubes-have-extra-v0-5641q6xozgca1.jpg

- Bambu Lab Community Forum. (n.d.). *Calibration Cube Overextrusion Example*.  
  https://cdn-forum.bambulab.com/optimized/2X/9/98fcf0afc59f416b30211358993ee74de4833d9c_2_1256x1000.jpeg

- Reddit. (n.d.). *XYZ Calibration Cube Surface Quality Comparison*.  
  https://preview.redd.it/xyz-calibration-cube-v0-uxoobnl22jeb1.jpg

- Reddit. (n.d.). *Strange Artifacts on Calibration Cube*.  
  https://preview.redd.it/strange-artifacts-on-calibration-cube-v0-gpndncumkb2c1.jpg

- Reddit. (n.d.). *XYZ Calibration Cube – X and Y Axis Problems*.  
  https://preview.redd.it/xyz-calibration-cube-x-and-y-problems-v0-l87hezvqyggc1.jpeg

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

94

<!-- SECTION: PAGE 96 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Aleneo de Droo University, Roes Ave. Publication District, Droo City, 8000 Droo, Jl. Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

95

<!-- SECTION: PAGE 97 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Alameda de Dania University, Roanoke Ave. Publication District, Dania City, 8000 Dania, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Course Title</th>
    <td>Basic Additive Manufacturing Laboratory Manual (3D Printing)</td>
  </tr>
  <tr>
    <th>Lesson No. and Title</th>
    <td>Laboratory 05: Support Strategies - Designing for Overhangs</td>
  </tr>
  <tr>
    <th>Learning Outcomes</th>
    <td>
      1. Understand the importance of supports<br>
      2. Optimize support strategies with:<br>
      &nbsp;&nbsp;a. Design considerations<br>
      &nbsp;&nbsp;b. Proper orientation<br>
      &nbsp;&nbsp;c. Support painting
    </td>
  </tr>
  <tr>
    <th>Time Frame</th>
    <td>This lesson can be finished in 1 HOUR.</td>
  </tr>
  <tr>
    <th>Lesson</th>
    <td>
      <strong>Bridging</strong><br>
      Not all overhangs are impossible to print. In some cases, a 3D printer can perform bridging, where it extrudes filament across a gap between two supported points. The filament is anchored on one end, spans the gap, and attaches to the opposite side, solidifying as it cools.<br><br>
      Proper cooling, print speed, and extrusion settings are crucial to prevent sagging. When tuned correctly, bridging allows certain overhangs or gaps to be printed cleanly without supports, reducing material use and post-processing time.<br><br>
      ![image](image_5.png)<br>
      <strong>Figure 1: Bridging</strong>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

96

<!-- SECTION: PAGE 98 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Angles

The need for supports can also be minimized or avoided by designing overhangs that do not exceed your printer’s optimal threshold angle. In general, most printers can handle overhangs up to **45 degrees** without significantly affecting print quality.

![image](image_5.png)

*Threshold angle: 30°*  
*Threshold angle: 25°*

**Figure 2: Threshold angle**

## Orientation

Another way to reduce or eliminate the need for supports is by adjusting the model’s orientation during slicing. This can be done by positioning the model so that it has the fewest possible overhangs.

![image](image_6.png) ![image](image_7.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_8.png) ![image](image_9.png) ![image](image_10.png) ![image](image_11.png)

---

97

<!-- SECTION: PAGE 99 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<div style="display: flex; align-items: center;">

<div style="width: 20%; background-color: #002868; height: 100%;"></div>

<div style="width: 80%; padding: 20px;">

![image](image_5.png)

**Figure 3: Optimal Orientation for Supports**

## Support Painting

Most slicers can automatically generate supports, making the process convenient and efficient for users. However, automated supports are not always optimized — they may add unnecessary structures that increase printing time and filament consumption. To improve efficiency, users can manually review and remove excess supports in areas where they aren’t needed.

For example, instead of placing supports along the entire length of an overhang, you can position them only at critical points, such as the edges or endpoints, and allow the printer to bridge the rest of the span. This approach not only saves material but also minimizes post-processing and potential surface damage caused by removing supports. Proper understanding of your printer’s bridging capabilities and fine-tuning slicer settings can greatly improve print quality while reducing waste.

</div>

</div>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

98

<!-- SECTION: PAGE 100 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Aleneo de Draco University, Rojas Ave. Publacion District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Figure 4.0: Auto Support

![image](image_5.png) ![image](image_6.png)

## Figure 4.1: Manual Support (Reduce)

![image](image_7.png) ![image](image_8.png)

Support painting isn’t only useful for reducing supports — in some cases, adding more is actually beneficial. In the example below, the model could theoretically print successfully since its overhangs are at a 45-degree angle, which most printers can handle without support. However, the model’s center of gravity shifts toward the extended

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_9.png) ![image](image_10.png) ![image](image_11.png) ![image](image_12.png)

99

<!-- SECTION: PAGE 101 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Rojas Ave. Publacion District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

overhang, increasing the risk of instability or toppling during printing. By strategically adding a support structure beneath the overhang, the model gains additional stability, ensuring a smoother print process and reducing the likelihood of print failure.

![image](image_5.png)

**Figure 4.2: Manual Support (Reinforce)**

To perform support painting, press [ L ] on your keyboard or click the Support Painting icon in Creality Slicer. Once activated, you can use the left mouse button to manually paint areas where you want supports to be added. Conversely, use the right mouse button to block or remove automatically generated supports in areas where they aren’t needed. This gives you precise control over support placement, helping you balance print stability, material efficiency, and surface quality.

![image](image_6.png)

**Figure 4.3: Support Painting**

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

100

<!-- SECTION: PAGE 102 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Droo University, Roos Ave, Publication District, Droo City, 8000 Droo, Jl Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Laboratory</th>
    <td>
      <strong>Step 1: Prepare the Model</strong><br>
      Go to the designated google drive for models and download the file named “Laboratory 05 - Supports”.

      <strong>Step 2: Slice</strong><br>
      Using all the lessons discussed. try to optimize the printing process with the least amount of support possible.<br><br>
      *Do not cut the objects into multiple parts*

      <strong>Step 3: Print</strong><br>
      Upload your Gcode and monitor the print to avoid issues.
    </td>
  </tr>
  <tr>
    <th>Advantages</th>
    <td>
      ➤ <strong>Enabling Complex Geometries:</strong> The primary advantage of supports is the ability to print designs with challenging features like overhangs, bridges, and intricate details that would otherwise be impossible to produce. They provide a foundation for parts of the model that don't have a lower layer to build upon, preventing them from collapsing during the printing process.<br><br>
      ➤ <strong>Increasing Print Success Rate:</strong> By providing a stable foundation for difficult geometries, supports significantly reduce the likelihood of print failures. This saves time, reduces material waste, and minimizes the frustration of having to restart a long print job.
    </td>
  </tr>
  <tr>
    <th>Disadvantages</th>
    <td>
      ➤ <strong>Increased Material Usage:</strong> Supports consume additional filament or resin, leading to higher material costs.<br><br>
      ➤ <strong>Longer Printing Time:</strong> Generating and printing supports significantly increases the total print duration.
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

101

<!-- SECTION: PAGE 103 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td>
      <ul>
        <li><strong>Post-Processing Required:</strong> Supports must be removed after printing, often requiring cutting, sanding, or dissolving — which adds labor and time.</li>
        <li><strong>Surface Damage Risk:</strong> Areas where supports contact the model may leave marks, rough surfaces, or small defects after removal.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><strong>Synthesis</strong></td>
    <td>
      <p>In this laboratory, you learned that support structures are fundamental to unlocking the full potential of 3D printing. They enable the fabrication of complex geometries with overhangs and bridges that would otherwise be impossible to produce. However, managing supports effectively goes beyond relying on automatic slicer functions—it requires strategic planning and thoughtful design.</p>
      <p>By understanding principles such as the 45-degree overhang rule, the limits of bridging, and the importance of proper model orientation, designers can significantly reduce the need for supports. Doing so saves material, minimizes print time, and simplifies post-processing. Additionally, the use of <strong>support painting</strong> offers precise manual control, allowing supports to be placed only where they are truly needed for structural stability. This targeted approach helps prevent unnecessary waste and reduces the risk of surface imperfections.</p>
      <p>Ultimately, this laboratory demonstrates that effective support management is a balance between achieving geometric freedom and optimizing the efficiency, quality, and sustainability of the final print.</p>
    </td>
  </tr>
  <tr>
    <td><strong>Reflection</strong></td>
    <td>
      <p>Learning how to use support structures is an important step in improving your 3D printing skills. It shows that printing isn’t just about creating the final object—it’s also about understanding the temporary parts that help make it possible. Just like scaffolding in construction, supports are only</p>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

102

<!-- SECTION: PAGE 104 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Driano University, Roanoke Ave. Publication District, Driano City, 8000 Driano, Del Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td rowspan="2" style="background-color: #002855; color: white; padding: 10px; vertical-align: top; width: 20%;">&nbsp;</td>
    <td>there for a while, but they play a big role in building something strong and complete.</td>
  </tr>
  <tr>
    <td>Thinking carefully about supports helps you become a smarter designer. Instead of always relying on automatic slicer settings, you start to plan ahead—seeing where problems might happen and finding ways to fix them before printing. Choosing whether to add supports or change the model’s orientation teaches problem-solving and helps you create cleaner, more efficient prints.<br><br>In the end, good support planning isn’t just about saving time or material—it’s about understanding how design, material, and the printer all work together. Being thoughtful with supports is a sign of a skilled creator who knows how to turn a design idea into a successful print.</td>
  </tr>
  <tr>
    <td style="background-color: #002855; color: white; padding: 10px; vertical-align: top; width: 20%;">FAQs</td>
    <td>
      <ol>
        <li><strong>Can supports affect print quality?</strong>
          <ul>
            <li>Yes. Supports prevent deformation and improve stability, but they can also leave marks or rough surfaces where they contact the model. Careful placement and removal are essential to maintain good surface quality.</li>
          </ul>
        </li>
        <li><strong>How can I make supports not affect print quality?</strong>
          <ul>
            <li>You can reduce the impact of supports on print quality by optimizing the Z-offset; Increasing the gap slightly allows the support to separate cleanly without fusing to the model.</li>
          </ul>
        </li>
        <li><strong>How do I make supports easier to remove?</strong>
          <ul>
            <li>Use a different material for supports: For example, print PLA models with PETG supports, as they don’t fuse together strongly.</li>
          </ul>
        </li>
      </ol>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

103

<!-- SECTION: PAGE 105 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Drooic University, Roesse Ave, Publication District, Drooic City, 8000 Drooic, Jel Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td>
      <ul>
        <li>Use dissolvable supports: Materials like PVA (for PLA) or HIPS (for ABS) can be dissolved in water or limonene, leaving a clean surface.</li>
        <li>Fine-tune Z-offset: A slightly higher support Z-offset allows supports to break away more easily without damaging the model.</li>
        <li></li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><strong>References</strong></td>
    <td>
      [1] “Supports settings,” Creality Wiki.  
      https://wiki.creality.com/en/software/update-released/Support/support-settings  
      [2] MadisonJames, “How to support effectively for complex 3D prints,” *Kingroon 3D*, Feb. 13, 2025.  
      https://kingroon.com/blogs/3d-printing-guides/how-to-support-effectively-for-complex-3d-prints
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

104

<!-- SECTION: PAGE 106 -->

Local Engine Failed: HTTPConnectionPool(host='192.168.1.91', port=8000): Read timed out. (read timeout=120)


<!-- SECTION: PAGE 107 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Rojas Ave, Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Course Title</th>
    <td>Basic Additive Manufacturing Laboratory Manual (3D Printing)</td>
  </tr>
  <tr>
    <th>Lesson No. and Title</th>
    <td>Laboratory 06: Single-Part Fabrication</td>
  </tr>
  <tr>
    <th>Learning Outcomes</th>
    <td>
      1. Optimize the 3D Model for single-part fabrication.<br>
      2. Evaluate the advantages and limitations of single-part fabrication.
    </td>
  </tr>
  <tr>
    <th>Time Frame</th>
    <td>This lesson can be finished in 1 HOUR.</td>
  </tr>
  <tr>
    <th>Introduction</th>
    <td>
      3D printers are best known for solving various challenges in traditional fabrication. If you look around your household, most furniture is assembled from multiple parts using nails, screws, or glue. This is mainly because many objects have complex geometries that make them difficult or even impossible to produce using traditional manufacturing methods. 3D printers, however, have far fewer limitations due to their operating mechanism. They can print complex objects as a single piece, making production faster and more efficient.<br><br>
      In this laboratory, we will explore how to optimize 3D models by applying various design considerations and slicing techniques.
    </td>
  </tr>
  <tr>
    <th>Lesson</th>
    <td>
      <strong>Maximizing Build Capacity</strong><br>
      Printing a model as a single piece is one of the most convenient ways to fabricate objects. It eliminates the need for assembly and ensures a clean, seamless finish. However, this approach is limited by your printer’s maximum build volume—the largest size it can print.<br><br>
      Some 3D models may initially appear too large for your printer, but with proper reorientation, the same design can often fit within the build plate. Rotating or tilting the model can help make single-piece printing possible. Choosing the right orientation not only helps the model fit, but also affects its strength, surface finish, and support requirements.
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

106

<!-- SECTION: PAGE 108 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave. Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<div style="display: flex; align-items: center;">

<div style="width: 20%; background-color: #002868; height: 100%;"></div>

<div style="width: 80%; padding: 20px;">

![image](image_5.png)

**Figure 6: Build Capacity**

## Design Considerations

When designing for single-part fabrication, it’s important to consider how supports will be added and removed. Avoid placing overhangs or intricate features in enclosed or hard-to-reach areas, as you won’t be able to remove supports once the model is printed.

Instead, optimize the design by adding gentle slopes, chamfers, or bridging-friendly shapes to reduce the need for supports altogether. If supports are necessary, plan them so they’re easy to access and remove without damaging the part. In short, design for printability and easy post-processing before starting the print.

## Strength

A limitation of single-part fabrication is that if one section breaks, the entire model must be reprinted since it isn’t modular. To prevent this, make sure your design is strong enough for its purpose, especially for load-bearing parts. This can be done by reinforcing weak areas, orienting the print correctly, and choosing appropriate infill and material settings.

</div>

</div>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

107

<!-- SECTION: PAGE 109 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Droo University, Roes Ave, Publication District, Droo City, 8000 Droo, Jl Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Orientation

Proper orientation is crucial for a resilient print. Always consider which direction the model will receive stress or force and align it so that layer lines run along the direction of force whenever possible. Prints are generally weaker between layers, so correct orientation greatly improves durability.

<div style="display: flex; justify-content: space-between;">

<div style="text-align: center; width: 45%;">

![image](image_5.png)

*Bending moment applying vertical shear stress between layers*

</div>

<div style="text-align: center; width: 45%;">

![image](image_6.png)

*Bending moment applying horizontal shear stress within layers*

</div>

</div>

**Figure 6.1: Anisotropy**

## Infill

The infill density should match the function of the print. For load-bearing applications, higher infill increases strength and rigidity. For purely decorative prints, high infill only wastes time and material. Selecting the right infill pattern can also help balance strength, weight, and print time.

## Material

Choosing the right filament is another key factor. Different materials have different properties—PLA is easy to print but brittle, PETG offers toughness and flexibility, and ABS provides better heat resistance. Select the material that best fits the purpose of your print.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

108

<!-- SECTION: PAGE 110 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Dania University, Rodeo Ave. Publication District, Dania City, 8000 Dania, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Laboratory</th>
    <td>
      <strong>Step 1: Prepare the Model</strong><br>
      Go to the designated google drive for models and download the file named “Laboratory 06 - Single-Part Fabrication”.

      <strong>Step 2: Slice</strong>

      <strong>Step 3: Print</strong><br>
      Upload your Gcode and monitor the print to avoid issues.
    </td>
  </tr>
  <tr>
    <th>Advantages</th>
    <td>
      ➤ <strong>Superior Structural Integrity and Strength:</strong> By eliminating joints, screws, welds, and other fasteners, a single printed part has fewer potential points of failure. The continuous layers of material create a more homogenous structure that can distribute stress more effectively. This often results in a part that is stronger, more rigid, and more durable than an equivalent assembled object.

      ➤ <strong>Streamlined Production and Reduced Assembly Time:</strong> The most direct benefit is the complete elimination of the assembly phase. This dramatically simplifies the manufacturing workflow, saving significant time and labor costs. A part that might have taken hours to assemble can come off the print bed ready for final use, freeing up personnel for other tasks.
    </td>
  </tr>
  <tr>
    <th>Disadvantages</th>
    <td>
      ➤ <strong>Build Volume Constraints:</strong> The most fundamental limitation is the physical size of the 3D printer's build volume. If a model's dimensions exceed the printer's capacity in any direction (X, Y, or Z), it simply cannot be printed as a single piece. This often necessitates splitting the model into smaller sections that can be printed individually and assembled later.

      ➤ <strong>Inefficient Orientation and Support Material Waste:</strong> Some designs have complex geometries that, regardless of their orientation on the build plate, will require extensive support
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

109

<!-- SECTION: PAGE 111 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Droo University, Roos Ave, Publication District, Droo City, 8000 Droo, Jl Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td>structures to print successfully. Printing large amounts of support material is not only time-consuming but also wastes a significant amount of filament. By strategically splitting a model, each component can be oriented in its most optimal position to minimize or even eliminate the need for supports, leading to faster prints and material savings.<br><br>➤ **Challenges with Maintenance and Repair**: If a single component of a monolithic object breaks, the entire part may need to be discarded and reprinted. In a modular, multi-part design, only the broken component needs to be replaced, making repairs simpler, faster, and more cost-effective.</td>
  </tr>
  <tr>
    <td><strong>Synthesis</strong></td>
    <td>In this laboratory, you explored the principles of single-part fabrication, a method that uses 3D printing’s unique ability to create complex, monolithic objects without assembly. While this approach offers important advantages such as improved structural integrity by removing weak joints and reduced production time, it also comes with critical design constraints.<br><br>Proper model orientation is essential, not only to fit a design within the printer’s build volume but also to maximize mechanical strength by aligning layer lines parallel to the direction of applied stress. Designing for printability also involves intentional choices such as adding chamfers or gentle slopes to minimize the need for supports, and selecting the right infill density and filament type based on the part’s purpose.<br><br>Ultimately, single-part fabrication requires a holistic design approach, where the designer considers the entire manufacturing process from model orientation and material selection to post-processing. This approach results in a final object that is both strong and efficiently produced.</td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

110

<!-- SECTION: PAGE 112 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Driano University, Roanoke Ave. Publication District, Driano City, 8000 Driano, Del Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Reflection</th>
    <td>This laboratory highlights that good design is not just about form or function, but also about understanding how an object is made. Single-part fabrication teaches the importance of designing with the manufacturing process in mind. Every decision—such as model orientation, infill settings, and material choice—affects how well a print performs once completed.<br><br>By recognizing the limitations of build volume, the direction of layer lines, and the role of supports, we learn to plan ahead and design more efficiently. These constraints are not barriers but opportunities to think critically and creatively.<br><br>Through this exercise, you also learned to value precision and foresight in engineering. The ability to anticipate printing challenges and make smart design adjustments early on leads to better-quality results and fewer printing failures. Single-part fabrication, therefore, strengthens not only technical skills but also problem-solving and decision-making—qualities essential in any field of design or engineering.</td>
  </tr>
  <tr>
    <th>FAQs</th>
    <td>
      <ol>
        <li><strong>Is single-part fabrication always better than modular printing?</strong>
          <ul>
            <li>Not always. While single-part fabrication improves strength and appearance, modular printing offers easier maintenance, repair, and color or material variation. The best approach depends on the part’s purpose and design requirements.</li>
          </ul>
        </li>
        <li><strong>Does single-part fabrication only apply to rigid models?</strong>
          <ul>
            <li>No, single-part fabrication is highly effective for creating non-rigid models with integrated flexibility and</li>
          </ul>
        </li>
      </ol>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

111

<!-- SECTION: PAGE 113 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Droo University, Roes Ave, Publication District, Droo City, 8000 Droo, Jl Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td>movement. This is achieved by designing compliant mechanisms, which are single-piece, jointless structures that generate motion from the elastic deformation of their flexible members.</td>
  </tr>
  <tr>
    <td></td>
    <td>Instead of using traditional assembled parts like bearings or hinges, a compliant mechanism is designed as a monolithic body where specific sections are intentionally made thin or shaped in a way that allows them to bend and flex. Additive manufacturing (3D printing) is exceptionally well-suited for this task, as it can produce the complex geometries required for these mechanisms in a single, uninterrupted process.</td>
  </tr>
  <tr>
    <td><strong>References</strong></td>
    <td>[1] Forge Labs, “Part orientation in 3D Printing | Forge Labs,” Forge Labs.<br>https://forgelabs.com/blog/part-orientation-3d-printing-comprehensive-guide<br>[2] C. Alexander, “The impact of part orientation on 3D print quality,” Formero, Oct. 21, 2025.<br>https://formero.com.au/how-part-orientation-affects-a-3d-print/</td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

112

<!-- SECTION: PAGE 114 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Aleneo de Droo University, Roes Ave. Publication District, Droo City, 8000 Droo, Jl Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

113

<!-- SECTION: PAGE 115 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Alameda de Dania University, Roanoke Ave. Publication District, Dania City, 8000 Dania, Jal. Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Course Title</th>
    <td>Basic Additive Manufacturing Laboratory Manual (3D Printing)</td>
  </tr>
  <tr>
    <th>Lesson No. and Title</th>
    <td>Laboratory 07: Modular Fabrication: Multi-Part Assembly Printing</td>
  </tr>
  <tr>
    <th>Learning Outcomes</th>
    <td>
      1. Explain the concept of modular fabrication in 3D printing.<br>
      2. Identify design strategies for splitting large models into smaller printable parts.<br>
      3. Demonstrate how to align, connect, and assemble multi-part 3D prints accurately.<br>
      4. Evaluate the advantages and limitations of modular fabrication for large-scale or functional designs.
    </td>
  </tr>
  <tr>
    <th>Time Frame</th>
    <td>This lesson can be finished in 1 HOUR and 30 MINUTES.</td>
  </tr>
  <tr>
    <th>Introduction</th>
    <td>
      Sometimes, a single 3D printer can’t print everything at once. What if your design exceeds the printer’s build volume or requires parts to be printed in different orientations, colors, or materials?<br><br>
      That’s where <strong>modular fabrication</strong> comes in. It’s a design approach where large or complex models are divided into smaller parts, printed separately, and then assembled like a puzzle. In this lesson, we’ll explore how modular 3D printing works, why it’s important in professional and maker settings, and how you can apply it in your own projects to make bigger, better, and smarter builds.
    </td>
  </tr>
  <tr>
    <th>Lesson</th>
    <td>
      Modular Fabrication means breaking down a model into multiple printable sections that can be later joined together. This allows designers to<br>
      <ul>
        <li>Overcome printer size limits</li>
        <li>Combine multiple materials or colors</li>
        <li>Replace or upgrade individual parts without reprinting the entire model</li>
      </ul>
      Think of it like LEGO pieces, where each has its own purpose but together, they form something greater!
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

114

<!-- SECTION: PAGE 116 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Rojas Ave, Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Design Considerations</th>
    <td>Imagine this, you’ve spent hours designing a detailed model for your project. When you hit “slice”, ready to print…only to realize your model is too big for your printer’s bed! Do you scale it down and lose detail? Or do you find another way?<br><br>When designing for modular printing, careful planning is key. A few simple strategies can make your prins stronger and easier to assemble.<br><br><strong>Part Orientation</strong> - Select the side of the part that will touch the build plate. A good orientation reduces supports, improves surface finish, and saves print time. As a good rule of thumb, place the largest flat surface on the bed to improve adhesion and reduce warping.<br><br><strong>Splitting Strategy</strong> - Cut model along flat, hidden, or natural seams. This keeps your assembly near and helps preserve the original look of your model. Avoid cutting through detailed areas to maintain appearance.<br><br><strong>Connection Types</strong> - You can design different ways for parts to fit together. This will depend on what suits best for your design. Here are a few examples of how it piece things together:<br><ul><li>Pins and Sockets - Simple plug and fit</li><li>Dovetail or Puzzle Joints - Prevent sliding or twisting</li><li>Threaded Inserts or Scews - For strong, detachable parts</li><li>Magnets or Clips - For quick assembly and easy removal</li></ul>This is not only applicable for bigger models, but also for systems made of separate, functional parts that work together.</td>
  </tr>
  <tr>
    <th>Adhesive and Fasteners</th>
    <td>When assembling 3D printed parts, choosing the right bonding method is essential. There are many types of connections. For permanent joints that you want to connect, you can use super glue or epoxy for a stronger connection. You can use threaded inserts or bolts if you want detachable</td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

115

<!-- SECTION: PAGE 117 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td>parts in your design. Make sure that you measure it accordingly, depending on your planned inserts/bolts to use. These methods provide flexibility depending on whether you need a temporary, semi-permanent, or permanent connection.</td>
  </tr>
  <tr>
    <td><strong>Laboratory</strong></td>
    <td>Now that you’ve already had an idea of the concept, let’s walk through how you can print and assemble a modular model.<br><br><strong>Step 1: Prepare the Model.</strong> Go to the designated Google Drive for models and download the file named “Laboratory 07 - Multipart Assembly”. Open your model in Creality Print and follow the next steps of this laboratory.<br><br>![image](image_5.png) Laboratory 07 - Multipart Assembly.stl ![image](image_6.png)<br><br><strong>Figure 1. STL file in Google Drive</strong></td>
  </tr>
  <tr>
    <td></td>
    <td><strong>Step 2: Slice Each Part</strong> Import the parts into Creality Slicer (Cura) and ensure flat surfaces are placed on the bed. Use these recommended settings for PLA:<br><br>![image](image_7.png)<br><br><strong>Figure 2.1 Recommended Settings for PLA</strong><br><strong>Layer Height:</strong> 0.2 mm<br><strong>Wall Loops:</strong> 2<br><strong>First Layer Speed:</strong> 50mm/s</td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_8.png) ![image](image_9.png) ![image](image_10.png) ![image](image_11.png)

---

116

<!-- SECTION: PAGE 118 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td><strong>Step 3: Print the Parts</strong></td>
  </tr>
  <tr>
    <td></td>
    <td>➤ <strong>Observe the Print:</strong> Monitor the printing process from time to time to avoid issues.</td>
  </tr>
  <tr>
    <td></td>
    <td><strong>Step 4: Assembly</strong></td>
  </tr>
  <tr>
    <td></td>
    <td>➤ <strong>Assemble the object:</strong> Remove the print from the bed and assemble it through inserting part A onto part B through the slots provided.</td>
  </tr>
  <tr>
    <td><strong>Advantages</strong></td>
    <td>➤ <strong>Flexible Beyond Size Limits:</strong> Modular fabrication enables printing projects larger than the printer’s build volume by dividing them into manageable parts that fit perfectly when assembled.<br><br>➤ <strong>Customizable and Upgradeable:</strong> Each component can be redesigned, replaced, or improved without reprinting the entire model — ideal for projects that evolve over time.<br><br>➤ <strong>Creative Material Combination:</strong> Designers can combine various materials, colors, or infill patterns to enhance both aesthetics and mechanical performance.<br><br>➤ <strong>Collaborative Fabrication:</strong> Multiple users can print different sections simultaneously and assemble them together — an effective approach for group or class projects.<br><br>➤ <strong>Supports Innovation and Learning:</strong> Encourages problem-solving, modular design thinking, and experimentation — essential skills in prototyping and engineering applications.</td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

117

<!-- SECTION: PAGE 119 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Rojas Ave. Publacion District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Disadvantages</th>
    <td>
      <ul>
        <li><strong>Time-Consuming Assembly:</strong> Printing parts separately requires additional time for preparation, alignment, and bonding during assembly.</li>
        <li><strong>Fit and Tolerance Issues:</strong> If clearances (typically 0.2–0.3 mm) are not carefully planned, seams may misalign or parts may not fit snugly, affecting overall quality.</li>
        <li><strong>Potential Weak Points:</strong> Joints and glued areas can become structural weaknesses if not reinforced or properly connected using the right adhesive or fasteners.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <th>Synthesis</th>
    <td>
      <p>In this laboratory, you learned how modular fabrication allows designers to create large or complex 3D models by dividing them into smaller, more manageable parts that can be printed separately and assembled with precision. This method combines design strategy, material understanding, and assembly techniques to achieve scalable and adaptable results.</p>
      <p>Ultimately, modular fabrication demonstrates how additive manufacturing goes beyond the limitations of printer size, promoting creativity, collaboration, and repairability. It reflects the engineering mindset of building complex systems from simple, well-designed parts—each piece contributing to a greater, functional whole. As you move forward, remember that the success of modular fabrication depends on accurate tolerances, proper alignment, and thoughtful design planning, turning what could be a simple print into a professional, functional assembly that embodies precision and innovation.</p>
    </td>
  </tr>
  <tr>
    <th>Reflection</th>
    <td>
      <p>Modular fabrication is a mindset—it teaches designers to think in parts, but build as a whole. Whether you’re making a drone arm, a robot body, or a simple pen holder, designing in modules helps you adapt, repair, and improve your work without starting from zero. In real-world engineering, modularity is everywhere—from smartphones with removable</p>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

118

<!-- SECTION: PAGE 120 -->
# PROJECT P.R.I.M.E

**Partnership in Robotics and Intelligent Machines for Education**

---

**Marsman Drysdale Foundation, Inc.**

---

**robotics@addu.edu.ph**

**(082) 221 2411**

**https://www.facebook.com/addugears**

---

components to satellites assembled in parts before launch. It’s how innovation becomes sustainable and scalable. Modular fabrication reminds us that innovation is rarely achieved alone. It’s not just about building objects—it’s about building systems that work together, where each part contributes to a greater purpose. In the same way, collaboration and community drive progress in technology and design. Every printed piece, idea, and contribution plays a role in creating something meaningful.

Through modular thinking, we learn patience, adaptability, and cooperation—the understanding that big results often come from small, well-designed parts working in harmony.

---

## FAQs

1. **Is modular fabrication only for large prints?**
   - No. It’s also for smaller, functional designs that need upgrades, movement, or replaceable parts

2. **How do I ensure parts fit properly?**
   - Leave small clearances (0.3–0.5 mm), use alignment pins, and test-fit before assembly [4].

3. **Can modular parts move or rotate?**
   - Yes. You can design hinges, clips, or screw joints for flexible or rotating assemblies

---

## References

[1] Autodesk Education, Design for Assembly: Modular 3D Printing Guide, 2023.

[2] Prusa Knowledge Base, Splitting Large Models for Printing, Prusa Research, 2022.

[3] All3DP, 3D Printing Assembly Techniques and Best Practices, All3DP Pro, 2023.

[4] Simplify3D, Improving Part Fit and Adhesion in Multi-Part Prints, Simplify3D Resources, 2023.

---

**robotics@addu.edu.ph**

**(082) 221 2411**

**https://www.facebook.com/addugears**

---

**Marsman Drysdale Foundation, Inc.**

---

**Page 119**

<!-- SECTION: PAGE 121 -->

Local Engine Failed: HTTPConnectionPool(host='192.168.1.91', port=8000): Read timed out. (read timeout=120)


<!-- SECTION: PAGE 122 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Rojas Ave, Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Course Title</th>
    <td>Basic Additive Manufacturing Laboratory Manual (3D Printing)</td>
  </tr>
  <tr>
    <th>Lesson No. and Title</th>
    <td>Laboratory 08: Kinematic Prints: Motion in a Single Build</td>
  </tr>
  <tr>
    <th>Learning Outcomes</th>
    <td>
      1. Understand the concept of print-in-place 3D printing and its mechanical principles.<br>
      2. Analyze and apply print orientation, clearance, and support considerations for moving parts.<br>
      3. Successfully fabricate a flexible model using the print-in-place technique.
    </td>
  </tr>
  <tr>
    <th>Time Frame</th>
    <td>This lesson can be finished in 1 HOUR and 30 MINUTES.</td>
  </tr>
  <tr>
    <th>Introduction</th>
    <td>
      One of the most fascinating capabilities of 3D printing is the ability to create moving parts in a single print, without assembly. This technique is called Print-in-Place (PIP), a design strategy where hinges, joints, or interlocking parts are printed already connected, yet remain freely movable once the print is complete.<br><br>
      Unlike traditional fabrication methods that require assembly using bolts, pins, or glue, print-in-place models rely entirely on precise design tolerances and printer accuracy.<br><br>
      In this exercise, you will explore this principle by printing a flexy model, a simple yet effective model that demonstrates flexibility achieved through carefully designed joints.
    </td>
  </tr>
  <tr>
    <th>Lesson</th>
    <td>Print-in-place models push the limits of FDM (Fused Deposition Modeling) 3D printers. Since all parts are printed together, the model must have proper clearances (small gaps) between the moving segments to prevent them from fusing together.</td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

121

<!-- SECTION: PAGE 123 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Rodeo Ave, Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td>
      To achieve successful movement, three main factors are considered:
      <ol>
        <li><strong>Clearance</strong> Each joint must have a <strong>small gap</strong> (typically 0.3–0.5 mm) between parts.
          <ul>
            <li>Too small → parts fuse together.</li>
            <li>Too large → parts become loose or floppy.</li>
          </ul>
          Proper clearance allows flexibility without breaking.
        </li>
        <li><strong>Orientation</strong> Print-in-place designs are best printed <strong>flat on the bed</strong>. This ensures that layers build up evenly and the flexible joints form properly without needing supports.</li>
        <li><strong>Supports</strong> Supports should be <strong>disabled</strong> in slicing. Print-in-place designs are made to be <strong>support-free</strong>, so that joints and hinges can move immediately after printing.</li>
      </ol>
    </td>
  </tr>
  <tr>
    <td></td>
    <td>
      <strong>Preparing the Model</strong><br>
      For the model, you can find print in place models online. For starters, there are less complex models available. For this laboratory, the model will be given for you to practice on.<br><br>
      <strong>Step 1: Download the Model</strong><br>
      Access the designated Google Drive folder, and download the file named “Laboratory 8 - Flexy.stl”

      <div style="background-color: #f0f0f0; padding: 10px; margin: 10px 0;">
        <strong>Name</strong><br>
        ![image](image_5.png) Laboratory 08 - Flexy.stl 📤
      </div>

      <strong>Figure 1.1 STL File in Google Drive</strong>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

122

<!-- SECTION: PAGE 124 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Rojas Ave. Publacion District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Step 2: Open in your slicer

Open the STL file using Creality Slicer.

![image](image_5.png)

*Figure 2.1 Importing the model into Creality Print*

---

## Step 3: Check Orientation

Make sure the model is positioned flat on the build plate.  
If it appears tilted or lifted, use the **Select Face to Lay Flat** tool to correct its orientation.

![image](image_6.png)

*Figure 3.1 Lay Flat Icon Tool*

This tool allows you to choose a specific face of your 3D model to align flat on the build plate.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

123

<!-- SECTION: PAGE 125 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## How to Use the Tool

1. Click the Select Face to Lay Flat icon on the top toolbar.
2. Your curses will change, click on the bottom face of the model.
3. The slicer will automatically rotate the model so that the selected face lies perfectly flat on the build plate.

*Tip: Always ensure the bottom face is flat before slicing to avoid print adhesion issues.*

![image](image_5.png)

**Figure 3.2 Select Face to Lay Flat**

---

## Step 4: Adjust Print Settings

Click on your model and set up your slicing parameters as follows. You can access these sections in the “Process” panel on the right-hand side of the slicer. Expand each category to modify its values.

- **Layer Height**: 0.2 mm
- **Infill Density**: 15–20%
- **Supports**: None
- **Material**: PLA (recommended for beginners)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

124

<!-- SECTION: PAGE 126 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Avenue de Drano University, Rovira Ave, Publication District, Drano City, 8000 Drano, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Figure 4.1 Recommended Print Settings Panel

![image](image_5.png)

---

## Step 5: Slice and Preview

Click Slice and inspect the layer view.

## Figure 5.1 Recommended Print Settings Panel

![image](image_6.png)

After slicing, switch to the Preview tab to review the print layers before exporting. Check that the joints show small gaps between sections, ensuring proper flexibility after printing.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

125

<!-- SECTION: PAGE 127 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Avenue de Drano University, Rovira Ave, Publication District, Drano City, 8000 Drano, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Figure 5.2 Print-in-Place Slicer Preview

In the Preview Mode, you’ll see the model color-coded by structure type. The G-code Preview Panel on the left side shows important details such as the estimated print time, material usage, and length, and the percentage of time per print section.

You can use the Vertical Slider (on the right side) to navigate through the layers and inspect how the model will be printed from bottom to top. Layer 1 shows the base adhesion, and the last layer should show the top surface pattern. Ensure no floating or disconnected layers appear — these would indicate poor contact or missing support.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

126

<!-- SECTION: PAGE 128 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Avenue de Drano University, Rovira Ave. Publication District, Drano City, 8000 Drano, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Figure 5.3 G-Code Preview

![image](image_5.png)

---

### Step 6: Save and Print

Export the G-Code File. Click the “Save to Disk” button. A save window will pop-up. This is where you save the final instruction file. Save this file directly to the USB or SD Card you will plug into the 3D printer. Print and observe the process, especially around the tail and spine segments where the flexible joints form.

### Step 7: Cooling and Removal

Once printing is complete, allow the model to cool for at least 5 minutes before removing from the print bed.

### Step 8: Flex Test

Gently bend the dinosaur to test its flexibility. Each segment should move freely without breaking or slicing apart.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

127

<!-- SECTION: PAGE 129 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Droo University, Roanoke Ave, Publication District, Droo City, 8000 Droo, Jol Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <thead>
    <tr>
      <th>Advantages</th>
      <td>
        <ul>
          <li><strong>No Assembly Required:</strong> The model is functional straight off the print bed.</li>
          <li><strong>Demonstrates Printer Precision:</strong> Perfect for understanding tolerances and layer adhesion.</li>
          <li><strong>Engaging and Educational:</strong> Encourages design thinking for real-world mechanisms like hinges or robotics joints.</li>
        </ul>
      </td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Disadvantages</th>
      <td>
        <ul>
          <li><strong>Printer Calibration Dependent:</strong> Poor bed leveling or extrusion inconsistencies may cause fused joints.</li>
          <li><strong>Not Suitable for All Geometries:</strong> Complex internal mechanisms may still need assembly.</li>
          <li><strong>Limited Repair Options:</strong> If one segment fails, the entire model may need reprinting.</li>
        </ul>
      </td>
    </tr>
    <tr>
      <th>Synthesis</th>
      <td>
        Print-in-place fabrication highlights the strength of additive manufacturing, producing motion in a single build. This laboratory helps students understand how clearance, orientation, and material properties affect movement and print success. In this lesson, you learned how <strong>motion can be built into a model</strong> through careful design, slicing, and calibration. Remember that success in kinematic printing depends on <strong>accurate spacing, clean bed adhesion, and good printer tuning</strong>.
      </td>
    </tr>
    <tr>
      <th>Reflection</th>
      <td>
        Print-in-place fabrication shows how design and precision work hand in hand to bring movement to life straight from the printer bed. Through this activity, you learned that even a simple flexible model requires careful planning, accurate clearances, and proper print orientation to succeed. 3D printing is not just about creating shapes, it’s about engineering functionality. The process can teach you to think critically about how parts interact, not just how they look. In real-world applications, this skill connects to robotics, product design, and mechanical systems where motion and accuracy are essential.
      </td>
    </tr>
  </tbody>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

128

<!-- SECTION: PAGE 130 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Alameda de Drago University, Rodeo Ave. Publication District, Drago City, 8000 Drago, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## FAQs

1. **What does “print-in-place” mean?**
   - A print-in-place model is designed to print as a single, complete object with built-in moving parts that don’t require post-assembly.

2. **Why shouldn’t I use supports?**
   - Supports can fuse into joints, preventing them from moving after printing.

3. **How can I make my own print-in-place design?**
   - You can use TinkerCAD, Fusion 360, or Onshape to create articulated parts with small gaps between them (0.3–0.5 mm clearance).

4. **What should I do if my dinosaur doesn’t move?**
   - Try gently flexing it after cooling, or adjust your slicer settings (check flow rate, nozzle temperature, and bed adhesion). You may also slightly increase the clearance for your next print.

---

## References

[1] DuitDesign. (n.d.). *Print-in-Place 3D Printing: How It Works and Best Practices*. Retrieved from www.duitdesign.com

[2] All3DP. (n.d.). *3D Printing Tolerances: How to Test & Improve Them*. Retrieved from https://all3dp.com/2/3d-printing-tolerances-test-fdm/

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

129

<!-- SECTION: PAGE 131 -->

Local Engine Failed: HTTPConnectionPool(host='192.168.1.91', port=8000): Read timed out. (read timeout=120)


<!-- SECTION: PAGE 132 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Dania University, Rodeo Ave. Publication District, Dania City, 8000 Dania, Jal. Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Course Title</th>
    <td>Basic Additive Manufacturing Laboratory Manual (3D Printing)</td>
  </tr>
  <tr>
    <th>Lesson No. and Title</th>
    <td>Laboratory 09: Adaptive Resolution: Variable Layer Techniques</td>
  </tr>
  <tr>
    <th>Learning Outcomes</th>
    <td>
      1. Learn how to properly adjust the layer height<br>
      2. Understand the advantages and limitations of variable layer height
    </td>
  </tr>
  <tr>
    <th>Time Frame</th>
    <td>This lesson can be finished in 1 HOUR.</td>
  </tr>
  <tr>
    <th>Introduction</th>
    <td>
      One of the most important qualities of a 3D-printed model is how smooth and detailed it looks. However, sometimes the curved parts of a print can appear rough or have visible layer lines. This usually happens when the printer uses the same layer height throughout the whole model, especially on areas with gentle slopes. In this laboratory, we will learn how to reduce this problem by using a slicer feature called variable layer height, which automatically adjusts the layer thickness to make curved surfaces look smoother and more refined.
    </td>
  </tr>
  <tr>
    <th>Lesson</th>
    <td>
      <strong>Reorient the model</strong><br>
      One effective way to reduce visible layer lines is to orient the object so that its slopes or curved areas are more parallel to the build plate. In this position, the printer can produce those surfaces using continuous, smoother extrusion paths, which results in a cleaner finish.
      <br><br>
      ![image](image_5.png)
      ![image](image_6.png)
      <br><br>
      <strong>Figure 1: Optimal Orientation for Curves</strong>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

131

<!-- SECTION: PAGE 133 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave, Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Adjust the layer height

Another way to improve surface quality is by decreasing the layer height. Smaller layers make each step less noticeable, producing a smoother appearance.

However, lowering the layer height for the entire model will also increase print time unnecessarily.

A better approach is to use Variable Layer Height, a feature available in Creality Slicer. This feature automatically adjusts the layer thickness throughout the model, using finer layers in curved or detailed areas and thicker layers in flatter regions, balancing print quality and printing time.

In Creality Slicer, you can choose to let the software automatically handle the variable layer height or manually edit the layer height values yourself.

- Automatic mode is great for quick and easy optimization.

![image](image_5.png)

**Figure 2.0: Variable Layer Height**

- Manual adjustment gives you more control if you want to fine-tune which parts of the model receive higher or lower resolution.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

132

<!-- SECTION: PAGE 134 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Avenue de Drano University, Rovira Ave, Publication District, Drano City, 8000 Drano, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td rowspan="2" style="background-color: #002855; color: white; padding: 10px; vertical-align: top;">
      <strong>Laboratory</strong>
    </td>
    <td>
      ![image](image_5.png)
      <p><strong>Figure 2.1: Manual Layer Height Adjustment</strong></p>
      <p>Both methods help you achieve smoother surfaces and better print quality while managing print time efficiently.</p>
    </td>
  </tr>
  <tr>
    <td>
      <h3>Part I: Fixed Layer Height</h3>
      <p><strong>Step 1: Prepare the Model</strong><br>
      Go to the designated Google Drive for models and download the file named “Single-Part Fabrication”.</p>
      <p><strong>Step 2: Slice</strong><br>
      Upload your file to the Creality Slicer and slice without using variable layer height</p>
      <p><strong>Step 3: Print</strong><br>
      Upload your Gcode and monitor the print to avoid issues.</p>
      <p><strong>Step 4: Observe</strong><br>
      Observe the output and identify areas that can be optimized using variable layer height.</p>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

133

<!-- SECTION: PAGE 135 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Alameda de Driano University, Rojas Ave. Publication District, Driano City, 8000 Driano, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Part II: Variable Layer Height

### Step 01: Prepare the Model

Go to the designated google drive for models and download the file named “Single-Part Fabrication”.

### Step 2: Slice

Upload your file in the Creality slicer and use variable layer height.

![image](image_5.png)

Using your output from **Part I: Fixed Layer Height** as a reference, optimize the model using variable layer height.

**Tip:**

Reduce the layer height in areas of your previous print that showed visible layer lines or coarse surface finish to improve the overall print quality.

Increase the layer height on flat or less detailed vertical sections to shorten printing time, compensating for the additional time needed in finer-detailed areas.

### Step 3: Print

Upload your Gcode and monitor the print to avoid issues.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

134

<!-- SECTION: PAGE 136 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Drano University, Raros Ave, Publication District, Drano City, 8000 Drano, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Advantages</th>
    <td>
      <ul>
        <li><strong>Enhanced Surface Quality:</strong> Variable layer height improves curved and sloped surfaces by automatically applying finer layers where geometry changes, significantly reducing visible stair-step artifacts.</li>
        <li><strong>Optimized Printing Time:</strong> Instead of using a single fine layer height across the entire model, adaptive slicing applies thicker layers on flat or vertical sections, maintaining visual quality while reducing print duration.</li>
        <li><strong>Reduced Post-Processing Needs:</strong> Smoother surfaces achieved through finer layers lessen the need for sanding or polishing, reducing post processing time.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <th>Disadvantages</th>
    <td>
      <ul>
        <li><strong>Adjusts height across the entire layer:</strong> One limitation of variable layer height is that it modifies the thickness of an entire layer rather than specific localized sections within that layer. As a result, when only a small portion of the model requires finer detail (such as curved areas), the rest of that layer is also printed at the reduced height. This can lead to longer print times for complex models with limited detailed regions</li>
      </ul>
    </td>
  </tr>
  <tr>
    <th>Synthesis</th>
    <td>
      <p>In this laboratory, you explored how adaptive resolution helps improve surface quality while keeping print time manageable. By comparing prints made using fixed and variable layer heights, you learned how thinner layers can make curves smoother while thicker layers speed up flat areas. Both automatic and manual adjustment methods were available in Creality Slicer, allowing students to choose between quick optimization and detailed customization.</p>
      <p>This experiment shows that adaptive/variable layer height is not only about improving how a print looks — it is also about learning how digital settings affect time, quality, and machine performance.</p>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

135

<!-- SECTION: PAGE 137 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Dania University, Rodeo Ave. Publication District, Dania City, 8000 Dania, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td>Understanding this balance is an important skill in professional 3D printing and modern manufacturing.</td>
  </tr>
  <tr>
    <td><strong>Reflection</strong></td>
    <td>In additive manufacturing, efficient use of resources is essential for achieving high-quality results. This activity demonstrates that quality does not depend solely on using the finest settings everywhere, but on applying them wisely where they matter most.<br><br>By identifying which sections of a model require thinner layers, we learn to allocate limited resources—such as time, filament, and effort—more effectively.<br><br>Through this process, students develop the skill of discerning where precision is necessary and where it can be optimized, leading to smarter, more sustainable 3D printing practices.</td>
  </tr>
  <tr>
    <td><strong>FAQs</strong></td>
    <td>
      <ol>
        <li><strong>Does variable layer height affect part strength?</strong><br>
          ○ Yes. Thicker layers can slightly reduce strength, while thinner layers improve bonding. For functional parts, finer layers are better in load-bearing sections.
        </li>
        <li><strong>When is manual adjustment better than automatic mode?</strong><br>
          ○ Manual editing is useful when the model has small details that automatic detection may miss, giving the user more control over which parts get finer layers.
        </li>
        <li><strong>Can adaptive layering cause problems with supports?</strong><br>
          ○ Yes, sometimes. Changing layer thickness can make the support contact uneven, leading to rough surfaces or harder removal. Always check the slicer preview before printing.
        </li>
      </ol>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

136

<!-- SECTION: PAGE 138 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Drooic University, Roes Ave. Publication District, Drooic City, 8000 Drooic, Jl Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## References

[1] M. Uyanik, S. A. Gungor, and O. Aydin, “Influence of layer thickness on mechanical properties of 3D printed PLA, PETG, and CF-PETG,” *Materials*, vol. 16, no. 13, p. 4574, 2023.

[2] “Print detailed objects faster using adaptive layers in Ultimaker Cura,” Ultimaker Learn, 2024. [Online]. Available: https://ultimaker.com/learn/print-detailed-objects-faster-using-adaptive-layers-in-ultimaker-cura

[3] “Adaptive layers in Cura: Explained,” All3DP, 2024. [Online]. Available: https://all3dp.com/2/cura-adaptive-layers-simply-explained

[4] “Cura adaptive layers (variable layer height),” Clever Creations, 2023. [Online]. Available: https://clevercreations.org/cura-adaptive-layers-variable-layer-height

[5] “Adaptive Layer height,” *Creality Wiki*. https://wiki.creality.com/en/software/update-released/toolbar-introduction/adaptive-layer-height

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

137

<!-- SECTION: PAGE 139 -->

Local Engine Failed: HTTPConnectionPool(host='192.168.1.91', port=8000): Read timed out. (read timeout=120)


<!-- SECTION: PAGE 140 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Droo University, Roanoke Ave, Publication District, Droo City, 8000 Droo, Jol Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Course Title</th>
    <td>Basic Additive Manufacturing Laboratory Manual (3D Printing)</td>
  </tr>
  <tr>
    <th>Lesson No. and Title</th>
    <td>Laboratory 10: Surface Engineering - Post-Processing for Quality</td>
  </tr>
  <tr>
    <th>Learning Outcomes</th>
    <td>
      1. Safely remove the 3D print from the build plate.<br>
      2. Understand the purpose and benefits of post-processing.<br>
      3. Properly execute a wet sanding technique to smooth a 3D printed part.
    </td>
  </tr>
  <tr>
    <th>Time Frame</th>
    <td>This laboratory activity can be finished in 30 MINUTES.</td>
  </tr>
  <tr>
    <th>Introduction</th>
    <td>
      Post-processing refers to any action or treatment performed on a 3D printed object after it has been removed from the printer. This process is crucial for transforming a raw print into a finished product by improving its surface finish, dimensional accuracy, and overall appearance. There are many methods of post-processing, ranging from simple support removal and sanding to more advanced techniques like vapor smoothing or painting.<br><br>
      In this activity, we will focus on one of the most effective and accessible methods for achieving a smooth, professional finish on your keychain: wet sanding.
    </td>
  </tr>
  <tr>
    <th>Lesson</th>
    <td>
      This lesson will guide you through the process of safely removing and finishing your 3D printed keychain. This is important because the removal part can “make” or “break” your print.<br><br>
      <strong>Safety First:</strong> Always be cautious when handling tools. If using a scraper, ensure the tool is angled away from your hands and body. Build plate is also hot, make sure to be caution when removing your print.
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

139

<!-- SECTION: PAGE 141 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave. Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Part A: Print Removal

### Step 1: Cool Down:
Allow the printer's build plate to cool down completely. Many modern build surfaces are designed to release prints easily once they are at room temperature.

### Step 2: Remove the Build Plate:
If your printer has a flexible or removable magnetic build plate, take it out of the printer.

![image](image_5.png)

### Step 3: Flex to Release:
Gently flex the build plate. You should hear the print pop loose. This is the safest way to remove a part.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

140

<!-- SECTION: PAGE 142 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave. Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<div style="display: flex;">

<div style="width: 20%; background-color: #002868; height: 100%;"></div>

<div style="width: 80%; padding: 20px;">

![image](image_5.png)

**Step 4: Use a Scraper (If Necessary):** If the print is still stuck, carefully slide a thin, dull scraper under a corner of the print. Keep the scraper low and parallel to the build plate and apply gentle, steady pressure. Never use excessive force.

**Part B: Wet Sanding**

Wet sanding uses water as a lubricant to prevent friction heat and to wash away sanded plastic particles, which prevents the sandpaper from clogging and results in a much smoother finish than dry sanding.

![image](image_6.png)

**Figure 3: Sandpaper**

</div>

</div>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_7.png) ![image](image_8.png) ![image](image_9.png) ![image](image_10.png)

---

141

<!-- SECTION: PAGE 143 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Alameda de Driano University, Roanoke Ave. Publication District, Driano City, 8000 Driano, Del Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

## Materials Needed:

- Your 3D printed keychain
- A small container of water
- Sandpaper of various grits (220, 400, 600, 1000, and 2,000)
- A paper towel or a cloth

## Procedure:

### Step 5: Prepare Your Area:
Lay down a paper towel to keep your workspace clean.

### Step 6: Start with Coarse Grit (Surface Leveling):
Take a small piece of the 220-grit sandpaper. Dip it into the water, and also apply a little water to the surface of your keychain.

![image](image_5.png)

### Step 7: Sand the Surfaces:
Using light pressure and a circular motion, begin sanding the flat surfaces and edges of your keychain. Your goal is to remove the visible layer lines. Keep the part and the sandpaper wet throughout the process.

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

142

<!-- SECTION: PAGE 144 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

Aleneo de Draco University, Raros Ave. Publication District, Draco City, 8000 Draco, Jal Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<div style="display: flex; align-items: center;">

<div style="width: 20%; background-color: #002868; height: 100%;"></div>

<div style="width: 80%; padding: 20px;">

![image](image_5.png)

**Step 8: Wipe and Inspect:** After a few minutes, wipe the part clean with your cloth. The layer lines should be significantly reduced, and the surface will have a matte, uniform appearance.

**Step 9: Move to Medium Grits (Smoothing):**

- **Step 9.1:** Switch to the 400-grit sandpaper and repeat the wet sanding process. This will remove the scratches left by the 220-grit paper.
- **Step 9.2:** Next, use the 600-grit sandpaper. This step will further refine the surface, making it feel very smooth to the touch.

**Step 10: Progress to Fine Grits (Polishing):**

- **Step 10.1:** Now, use the 1000-grit sandpaper. This step moves from smoothing to polishing, removing the finest scratches and starting to bring a slight sheen to the plastic.
- **Step 10.2:** Finally, use the 2000-grit sandpaper. This is the final polishing step. It will create a highly smooth, semi-gloss surface.

</div>

</div>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_6.png) ![image](image_7.png) ![image](image_8.png) ![image](image_9.png)

---

143

<!-- SECTION: PAGE 145 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Roca Ave, Publication District, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <td></td>
    <td><strong>Step 11: Clean and Dry:</strong> Once you are satisfied with the finish, thoroughly rinse your keychain with water to remove all remaining plastic dust and let it dry completely.</td>
  </tr>
  <tr>
    <td><strong>Advantages</strong></td>
    <td>
      <ul>
        <li><strong>Superior Surface Finish:</strong> Wet sanding is highly effective at eliminating layer lines, resulting in a smooth, almost injection-molded appearance that is difficult to achieve with other basic methods.</li>
        <li><strong>Prevents Clogging and Dust:</strong> The water acts as a lubricant and cleaning agent, washing away plastic dust. This prevents the sandpaper from getting clogged and eliminates the inhalation of airborne microplastic particles.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><strong>Disadvantages</strong></td>
    <td>
      <ul>
        <li><strong>Messy Process:</strong> As the name implies, it involves water and plastic particle slurry, which can be messy to work with and requires a dedicated workspace and cleanup.</li>
        <li><strong>Time-Consuming:</strong> The process is entirely manual and can be laborious, especially for larger or more complex parts. It requires patience to work through the different grits of sandpaper.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><strong>Synthesis</strong></td>
    <td>
      You have now completed the final, transformative step of the 3D printing process: <strong>Post-Processing and Finishing.</strong><br><br>
      A raw 3D print is functional, but its quality is truly revealed in the finishing touches. Proper print removal prevents damage, methodical sanding removes imperfections, and progressing through finer grits creates a professional finish.<br><br>
      Remember: “<em>A well-finished part is the mark of true craftsmanship.</em>”
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

144

<!-- SECTION: PAGE 146 -->
# PROJECT P.R.I.M.E

*Partnership in Robotics and Intelligent Machines for Education*

*Aleneo de Draco University, Rojas Ave. Publacion Distric, Draco City, 8000 Draco, Jal Sur*

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr>
    <th>Reflection</th>
    <td>Why is post-processing an important skill, even when the 3D printer produces a dimensionally accurate part? If you skip the finishing steps or use the wrong sanding technique, how might the final object's quality, appearance, and feel be compromised?<br><br>Through this activity, you learn that excellence is in the final details. Taking time to properly finish a product reflects diligence, care, and a commitment to quality, which are values essential in both engineering practice and personal growth.</td>
  </tr>
  <tr>
    <th>FAQ</th>
    <td>
      <ol>
        <li><strong>Why do my 3D prints have visible layer lines?</strong>
          <ul>
            <li>Layer lines are a fundamental characteristic of Fused Deposition Modeling (FDM) 3D printing. The printer builds the object by depositing material one layer at a time, and the visible lines are the edges of these individual layers.</li>
          </ul>
        </li>
        <li><strong>Do I have to start with 220-grit sandpaper?</strong>
          <ul>
            <li>Yes, starting with a lower grit (like 220) is important for efficiently removing the coarse layer lines. You must progress from coarse grits for removing lines to progressively finer grits (like 1000 and 2000) for achieving a polished, high-gloss finish.</li>
          </ul>
        </li>
        <li><strong>Can I paint my model after sanding?</strong>
          <ul>
            <li>Yes. Sanding is a critical preparation step for painting. A well-sanded surface provides a better texture for the paint and primer to adhere to, resulting in a much more professional-looking final product.</li>
          </ul>
        </li>
        <li><strong>Can I paint my model after sanding?</strong>
          <ul>
            <li>Yes. Sanding is a critical preparation step for painting. A well-sanded surface provides a better texture for the paint</li>
          </ul>
        </li>
      </ol>
    </td>
  </tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

145

<!-- SECTION: PAGE 147 -->
# PROJECT P.R.I.M.E

**Partnership in Robotics and Intelligent Machines for Education**

---

**Marsman Drysdale Foundation, Inc.**

---

**robotics@addu.edu.ph**

**(082) 221 2411**

**https://www.facebook.com/addugears**

---

<table>
  <thead>
    <tr>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>**References**</td>
      <td>and primer to adhere to, resulting in a much more professional-looking final product.</td>
    </tr>
    <tr>
      <td>[1] Sinterit, “3D printing sanding guide: how to smooth your 3D prints,” Sinterit. [Online]. Available: https://www.sinterit.com/3d-printing-sanding-guide-how-to-smooth-your-3d-prints/.<br>[2] All3DP, “Sanding 3D Prints: How to Sand PLA &amp; More,” All3DP. [Online]. Available: https://all3dp.com/2/sanding-3d-prints-a-beginners-guide/.<br>[3] Unionfab, “How to Sand 3D Prints? A Beginner's Guide,” Unionfab, Oct. 18, 2024. [Online]. Available: https://www.unionfab.com/blog/how-to-sand-3d-prints/.</td>
      <td></td>
    </tr>
  </tbody>
</table>


---

**robotics@addu.edu.ph**

**(082) 221 2411**

**https://www.facebook.com/addugears**

---

**Marsman Drysdale Foundation, Inc.**

---

**146**

<!-- SECTION: PAGE 148 -->
# PROJECT P.R.I.M.E

Partnership in Robotics and Intelligent Machines for Education  
Aleneo de Droo University, Roes Ave. Publication District, Droo City, 8000 Droo, Jl Sur

---

**Marsman Drysdale Foundation, Inc.**

![image](image_1.png) ![image](image_2.png) ![image](image_3.png) ![image](image_4.png)

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

<table>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
  <tr><td></td><td></td></tr>
</table>

---

📧 robotics@addu.edu.ph  
📞 (082) 221 2411  
🌐 https://www.facebook.com/addugears

---

**Marsman Drysdale Foundation, Inc.**

![image](image_5.png) ![image](image_6.png) ![image](image_7.png) ![image](image_8.png)

---

147
