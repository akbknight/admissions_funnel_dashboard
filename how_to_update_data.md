# 🍼 The Super-Simple "Explain It Like I'm 5" Guide: Updating the Admissions Dashboard

Welcome! This guide is going to show you exactly how to update our dashboard with new numbers. Think of the dashboard like a magic coloring book, and you are about to give it new colors!

---

## 🎨 Getting Your Crayons Ready (Prerequisites)
Before we start, you need two tools on your computer:
1. **Git** (This helps us save our work to the internet) -> [Download here](https://git-scm.com/downloads)
2. **Python 3.8+** (This is the engine that does all the math for us) -> [Download here](https://www.python.org/downloads/)

---

## Step 1: Copy the Project to Your Computer 💻
Right now, the project lives inside a big clubhouse on the internet called **GitHub**. We want to bring a copy of it down to your computer so you can play with it.

1. Open up your "Terminal" (Mac) or "Command Prompt" (Windows)—it looks like a little black box where you can type things.
2. Tell the computer to grab the project by typing this and hitting Enter:
   ```bash
   git clone https://github.com/akbknight/admissions_funnel_dashboard.git
   ```
3. Now, walk into that folder you just downloaded by typing:
   ```bash
   cd admissions_funnel_dashboard
   ```
4. Finally, tell Python to unpack all the tools we need:
   ```bash
   pip install -r requirements.txt
   ```

---

## Step 2: Feed the Dashboard New Files 📂
The dashboard is hungry for new data! You have two shiny new Excel files:
1. The new Fall 2026 file (Example: `Fall 2026 Application Data as of [Date].xlsx`)
2. The old Fall 2025 file (Example: `Recruit Exported Enrollment - F25 to F26 - AI Opp Funnel.xlsx`)

**What to do:**
Drag and drop both of those Excel files into the folder named `data`, and then into the folder named `raw`. Done!

---

## Step 3: Tell Python the Names of Your New Files 📝
Python doesn't know what you named your new files yet. We have to tell it!

1. Open the file called `data_pipeline.py` using a text editor (like Notepad, or VS Code).
2. Right near the top (around lines 17 & 18), you will see sentences wrapped in quotes like this:
   ```python
   F26_FILE = os.path.join(RAW_DIR, "Fall 2026 Application Data as of 2.13.26.xlsx")
   F25_FILE = os.path.join(RAW_DIR, "Recruit Exported Enrollment - F25 to F26 - AI Opp Funnel.xlsx")
   ```
3. Change the names inside the quotes to perfectly match the names of the Excel files you just dragged into the folder. Save the file!

---

## Step 4: Press the "Magic Blender" Button 🌪️
Now it's time to let Python do all the hard math. 

Go back to your little black box (Terminal/Command Prompt) and type:
```bash
python data_pipeline.py
```
Hit Enter! Python will chew up the Excel files, do a bunch of counting, and spit out the nice clean numbers that the dashboard needs.

---

## Step 5: Test It Out! 🔍
Let's make sure nothing broke. In that same black box, type:
```bash
streamlit run app.py
```
A webpage should pop up on your computer. Look around! Are the new numbers showing up correctly? If yes, great job!

---

## Step 6: Send It Back to the Internet 🚀
The very last step is to send your updated work back up to the internet so that everyone else can see it on the live link.

In your black box, type these three commands, pressing Enter after each one:
```bash
git add .
git commit -m "I added new data to the dashboard!"
git push origin main
```

**And you are done!** 🥳
Within a few minutes, the live dashboard on Streamlit will magically refresh itself and show the whole world your brand new numbers! You can view the live dashboard directly here: [Live Admissions Dashboard](https://admissionsfunneldashboard-8pbzttpynneixaywcls7rx.streamlit.app/)
