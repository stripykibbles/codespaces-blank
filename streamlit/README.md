# THE PERFECTIONISM BUSTER !!
#### Beat the habit of spending time editing your work when you should be writing more of it with this minimalist interface created with Python.
Video Demo: [HERE](https://youtu.be/AyReSnJTIfI)



## Overview
Writing is hard, and it can be even harder if you have the bad habit of over-editing your work; the longer your project becomes, the harder it is to make progress, since the more of it there is to edit.

Enter this program. Written in Python (with a sprinkling of HTML, CSS, and JavaScript) for Harvard University's CS50's Introduction to Programming with Python online course through EdX, its purpose is to help users overcome perfectionist tendencies and make their writing sessions as productive as possible via two main methods.

First, its Streamlit-based user interface is super minimalist. The main page is devoid of bells and whistles, and you only have three fonts to choose from, so no more procrastinating by fussing with the formatting.

The second method has to do with the unique way by which the program saves and displays data. When you finish a writing session and click the button to save your work, you're prompted to enter a quick summary of what you've just written. The entry and summary are then saved to a CSV file on the backend of the program, and the text input area is cleared. When you relaunch the program to pick up where you left off, instead of seeing what you previously wrote (as you would with a typical word processor like Microsoft Word or Google Docs), you can only see the summaries, which are non-editable and displayed in reverse chronological order. This way, you have a record of what you've already covered to jog your memory, but you aren't tempted to spend time editing your work in lieu of making progress. The only thing the program allows you to do is continue writing.

Of course, when you come to the end of your project (or if you really want to see what you've written), you can export your entries as a TXT file. You can also export the raw data, summaries and timestamps included, as a CSV file. Now that you've gotten all your ideas down on the page, you can continue polishing them to your heart's content in the word processor of your choosing.

Happy writing!



## App Flow
When first launching the program, you will see a page with a text input area as its only element. Entries will be written here.

In order to keep the main page as minimalist and distraction-free as possible, all menu buttons, including the button to save your work, can be found in the collapsible sidebar on the left.

The sidebar's exact contents will change depending on whether you are starting a new project or resuming an existing project, though some elements are present no matter what. The elements inside the sidebar are as follows:

#### Word Count
A running tally of the words you've submitted so far. The default value, of course, is zero.

#### Submit & Clear Text Area
This button opens a dialog box in which you may add a summary of your entry to reference in the future. The summary has a character limit equal to one-third of the character length of the original entry. From this dialog box, clicking "Submit" will prompt the program to check if a CSV file for your project already exists. If not, it will create one. Next, it appends the entry and summary to the CSV file, along with the submission's timestamp and a word count for the entry. Lastly, the text input area on the main page is cleared and reset.

#### View Summary
When you click this button, the program pulls all summaries from the CSV file and displays them in reverse chronological order, with the corresponding submission dates as headers.

#### Export Work
You can export your work to date as a TXT file that contains only the entries. Alternatively, you can download the raw CSV file that contains the entries along with their timestamps, word counts, and summaries.

#### Import Work
Both TXT and CSV files can be imported into the program. While TXT files may be imported regardless of their origin, only CSV files created by this program (i.e. with specific fieldnames) are accepted. Importing a TXT file will simply add the content of the file to the text input area; users will still need to click Submit & Clear Text Area in order to add a summary to the new content. (Clicking Import Work again before clicking Submit & Clear Text Area will overwrite the contents of the text input area.) In contrast, if users submit a CSV file, the text input area will not be filled. Instead, users will need to click View Summary to view summaries and dates of their recent entries.

#### Settings
You can select from three font options: sans serif (Atkinson Hyperlegible Next), serif (Crimson Text), or monospace (Courier Prime).



## Setup
In its current iteration, this program is designed to run on local Python environments.

To install the required libraries, run the following pip command:

```
pip install -r requirements.txt
```

To launch the streamlit app, run this command:

```
streamlit run project.py
```



## Libraries Used
- **streamlit:** An open-source Python framework that allows developers to create graphical user interfaces (GUIs) for web applications.
- **streamlit.components.v1:** A module within the Streamlit library that enables embedding HTML in Streamlit applications.
- **csv:** Provides tools for reading and writing CSV files.
- **datetime:** Used in this program to record the date and time that an entry is submitted.
- **os.path:** Provides a way to interact with the operating system. Used in this program to determine if the user is starting a project for the first time (i.e. "novel.csv" does not exist) or is resuming an existing project (i.e. "novel.csv" does exist).
- **re:** Provides support for regular expressions. Used in this program to parse timestamps created with the datetime module.
- **io:** Provides tools for working with input/output (I/O) streams and managing file-like objects. When users upload a file via Streamlit, this program uses io to convert the resulting UploadedFile object to a format readable by csv.DictReader.

> [!NOTE] Two other GUIs I considered using were NiceGUI and tkinter, Python's standard GUI toolkit. I chose Streamlit because it was quick to jump into, with documentation that was easy for me to understand and navigate.


## Project Structure
- **project.py:** The main program, which contains the following functions:
  - **main:**
    - This function starts by calling check_rerun and check_font to initialize the page (more on those two functions below).
    - It then adds the sidebar and main text area.
    - Lastly, it includes a bit of JavaScript that adds an EventListener to the text area, to help make sure users don't accidentally navigate away and lose their progress.
  - **sidebar:**
    - The sidebar always calls get_words and dialog_settings.
    - It also has a button to Submit & Clear Text Area. When users click this button, it tests to see if the text input area contains any content. If it does, it calls dialog_submit. If it doesn't, it displays a message saying users have to write something first.
    - If "novel.csv" does not exist (i.e. users are starting a new project), a button that allows users to import their work is shown. Pressing this button will trigger dialog_import.
    - If "novel.csv" does exist (i.e. users are working on a project in progress), two alternate buttons are shown: View Summary, which triggers dialog_summary, and Export Work, which triggers dialog_export.
  - **dialog_settings:**
    - This function opens a dialog box containing a dropdown menu. The contents of the dropdown menu are pulled from a dict named font_options that contains font names, font sizes, and font categories (e.g. sans serif, serif, monospace). Changing the selection of the dropdown menu will trigger check_font. Clicking a button to Save & Close will close the dialog box by triggering an app rerun. (This is the only way to programmatically close a dialog box in Streamlit.)
  - **check_font:**
    - Explaining this function requires explaining how Streamlit stores and shares variables across app reruns. This is done using Streamlit's Session State API, which functions like a Python dictionary with key/value pairs.
    - The function starts by checking whether the key "font" already exists in Session state with `if "font" in st.session_state`. If it doesn't – meaning this is the first time the user has loaded the page – the value of st.session_state["font"] is set to "Sans Serif" by default.
    - The value of st.session_state["font"] is then assigned to a variable called font, and an f-string with custom CSS is updated using the information from the font_options dict (ex. `font-family: {font_options[font]["name"]}` and `font-size: {font_options[font]["size"]}`).
  - **dialog_import:**
    - This function opens a dialog box with a file uploader that accepts TXT and CSV files.
    - When a file is uploaded, the function checks its extension with os.path.splitext, and a button appears that allows users to finish importing the file.
    - If the extension is TXT, the button will say Save & Keep Working. Clicking this button will add the contents of the TXT file to the text input area on the main page, clear the file from the file uploader, and close the dialog box via an app rerun.
    - If the extension is CSV, the button will say Save & Close. Clicking this button will trigger the import_csv function.
  - **import_csv:**
    - This function takes an UploadedFile object from the Streamlit uploader as a parameter. It then uses io.TextIOWrapper and csv.DictReader to determine if the uploaded CSV file was exported by this program by comparing its fieldnames. If the fieldnames are correct, it creates a new CSV with the imported data, clears the file from the file uploader, and closes the dialog box via an app rerun.
  - **dialog_export:**
    - This function opens a dialog box with two download buttons allowing users to download their data in TXT or CSV format. If the user clicks the Export Raw Data button, the download of the CSV file begins right away. Compiling only the entries requires one additional step, so clicking the Export Text button will trigger the export_text function.
  - **export_text:**
    - This function compiles all entries in the novel.csv file into a single string separated by line breaks. It then creates a TXT file named novel.txt, writes the string into the file, and returns the file.
  - **dialog_summary:**
    - This function opens a dialog box where users can view all of their summaries sorted by date in reverse chronological order. It converts the CSV file into a dictionary and uses f-strings in combination with HTML to append each summary to a list like so: `summary.append(f'<dt>{date_format(row["date"])}</dt><dd><p>{row["summary"]}</p></dd>')` The list is then rendered in HTML: `st.markdown(f"""<dl>{my_string}</dl>""",unsafe_allow_html=True)` Styling the `<dl>`, `<dt>`, and `<dd>` tags with CSS elsewhere in the program allows dates and summaries to be formatted and displayed programmatically.
  - **dialog_submit:**
    - This function opens a dialog box with a text input area and prompts users to add a summary of what they've just written.
    - The character limit of the text input area is determined by the get_characters function.
    - If users click the Submit button, the submit function is triggered, followed by an app rerun to close the dialog box.
  - **submit:**
    - This function takes the value of the main text input area and assigns it to a variable called entry. It then uses `len(entry.split(" "))` to determine the word count of the entry. Next, it takes the value of the text input area from the summary dialog box and assigns it to a variable called summary. It then uses two functions, datetime.now (from the datetime module) and date_parse, to determine the current date and time.
    - Next, the function checks if novel.csv exists. If it doesn't, it creates a new CSV file and appends the fieldnames along with the values of the date, time, entry, entry_word_count, and summary variables. If novel.csv exists, it skips the step of adding the fieldnames and simply adds the five variables.
    - Lastly, it clears the contents of the text input area on the main page and sets the value of st.session_state["rerun"] to True (more on that below).
  - **check_rerun:**
    - I created this function because I wanted to display a message to the user confirming that their work was successfully submitted. However, whenever a user clicks a button on a Streamlit page, the entire app runs again from top to bottom. If I programmed the button to display an alert, the alert would disappear immediately when the app reran. I had two options: delay the time between the alert appearing and the app rerunning using something like time.sleep, or find a workaround that would allow me to display the alert after the app reran.
    - I decided the second approach was preferable, but it meant I would have to create and store a variable in st.session_state in order to make sure the app knew to display the alert immediately after a rerun. I named this variable st.session_state["rerun"].
    - When the page is first initialized, st.session_state["rerun"] is set to False. The only time it is ever set to True is at the end of the submit function, i.e. right after the user submits an entry.
    - If the page reruns and the value of st.session_state["rerun"] is False, nothing happens. However, if the value is True, meaning the user has just submitted an entry, the page displays an alert confirming that their entry has been logged, i.e. the submit function has finished running. After the alert is displayed, the value of st.session_state["rerun"] is set back to False.
  - **get_words:**
    - This function iterates through novel.csv (if it exists) to determine how many words the user has submitted, by adding up the values in the entry_word_count column. If novel.csv does not exist, the value defaults to zero.
    - The function then displays an encouraging message depending on how many words the user has submitted.
  - **get_characters:**
    - This function takes a string as a parameter. It calculates the length in characters of the string, divides that number by 3, and assigns it to a variable called chars. If chars is less than 50, the value of chars is set to 50. The function then returns chars.
  - **date_parse:**
    - This function takes a datetime object from the datetime module as a parameter. Using regular expressions, it separates the datetime object into two strings, one for the date and one for the time, and then returns those two strings.
  - **date_format:**
    - This function takes a string – the date string returned by the date_parse function – as a parameter. Using regular expressions, it reformats it from a MM-DD-YYYY format to a Month DD, YYYY format, in order to be displayed in the view_summary dialog box.
- **README.md:** This document.
- **requirements.txt:** A list of libraries required to run the program.
- **test_project.py:** Unit tests for the program.
- **novel.txt:** An example of the structure of the TXT files generated by this program. All credit and kudos to the mother of science fiction herself, Mary Shelley, for the content.
- **novel.csv:** An example of the structure of the CSV files generated by this program.

> [!NOTE] One unique aspect of the Streamlit platform is that seemingly minor interactions with the app, such as clicking a button to open a menu, can trigger full app reruns. This is usually not noticeable to the user. To help keep track of what parts of the app are rerunning and when, the program prints the name of each function as they run in the terminal for troubleshooting purposes only.


## Future Improvements
- Explore deploying the app on Streamlit so that users can access it via the web as opposed to having to run it locally. The way the program creates and stores files may need to be revisited if they are being stored on Streamlit's servers as opposed to the user's local machine.
- Allow users to name or title their projects. Project titles could be displayed in the sidebar and perhaps be reflected in the filenames of exports, which currently default to "novel.csv" and "novel.txt."
- Allow users to select between Light or Dark mode and increase or decrease the font size in the Settings section.
- Add more unit tests covering additional functions to test_project.py. A little Googling indicates there are methods for creating unit tests for File IO functions, but CS50P didn't cover them, so I would need to return to this after some additional research and autodidacticism.
- Potentially allow users to opt into a feature whereby summaries of their entries are generated programmatically by AI, to avoid making them write summaries themselves.



## Acknowledgments
I would like to acknowledge and thank Professor David J. Malan and the rest of the team behind Harvard University's CS50 Introduction to Programming with Python for providing this amazing learning experience and opportunity.

I'd also like to thank my dad, who took CS50P along with me. Our video chats gave me the motivation to find the time for and push through tough problem sets, and I always had fun and learned a lot from comparing our approaches afterward. We've come a long way from playing Solitaire on Windows 95 and learning about JavaScript from a book. Next up: Python and AI!

Love you, Dad!
