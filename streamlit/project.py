import streamlit as st
import streamlit.components.v1 as components
import io
import csv
import os.path
import re
from datetime import datetime



if "run_number" not in st.session_state:
    st.session_state["run_number"] = 1
else:
    st.session_state["run_number"] += 1
print("Run Number: ", st.session_state["run_number"])



#https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
st.set_page_config(page_title="Typewriter", layout="wide", initial_sidebar_state="collapsed")



#https://discuss.streamlit.io/t/text-input-how-to-disable-press-enter-to-apply/14457/6
#<div data-testid="InputInstructions"><span>Press ⌘+Enter to apply</span><span>0/1</span></div>
st.markdown("""
    <style>
    div [data-testid="InputInstructions"] span + span {
        background-color: #e4e4e4 !important;
        border-right: 3px #e4e4e4 solid !important;
        border-left: 3px #e4e4e4 solid !important;
    }
    div [data-testid="InputInstructions"] > span:nth-child(1) {
        visibility: hidden;
    }
    div [data-testid="InputInstructions"] > span + span::before {
        content: "Character limit: " !important;
        margin: 0px !important;
    }
    [role=dialog] {
        padding-left: 10px;
        padding-right: 10px;
        padding-bottom: 10px;
    }
    [role=dialog] div [data-testid="stVerticalBlock"] button {
        background-color: #ebebeb;
    }
    [role=dialog] div [data-testid="stVerticalBlock"] button:hover {
        background-color: #dbdbdb;
    }
    [role=dialog] div [data-testid="stFileUploaderFile"] button {
        background-color: #ffffff !important;
    }
    [role=dialog] div [data-testid="stFileUploaderFile"] button:hover {
        background-color: #ffffff !important;
    }
    div [data-testid="stHeader"] {
        margin-bottom: 16px;
    }
    div [data-testid="stToast"] {
        background-color: #e4e4e4;
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
    }
    svg {
        fill: black !important;
    }
    div [data-testid="stMainBlockContainer"] {
        padding-top: 35px;
        padding-bottom: 50px;
    }
    textarea {
        resize: none !important;
        padding: 0px !important;
        &div [data-testid="stMainBlockContainer"] {
            width: 800px !important;
            height: 800px !important;
        }
    }
    div [data-testid="stSidebar"][aria-expanded="true"] {
        width: 250px !important;
    }
    div [data-testid="stSidebarHeader"] {
        margin-bottom: 8px !important;
    }
    div [data-testid="stSidebarContent"] {
        overflow: hidden;
        text-align: center;
        padding: 0px;
    }
    div [data-testid="stVerticalBlock"] {
        align-items: center;
    }
    dl {
        max-height: 70vh;
        margin-bottom: 10px;
        padding-right: 10px !important;
        overflow: auto;
        scrollbar-color: #e4e4e4 white !important;
    }
    div [data-testid="stMarkdownContainer"] dt {
        width: fit-content !important;
        height: fit-content !important;
        padding: 0px 10px 0px 10px;
        background-color: #e4e4e4;
        color: #75767d;
        font-size: 75% !important;
    }
    div [role="dialog"] svg {
        margin-top: -5px !important;
        color: #75767d !important;
    }
    dd {
        margin: 0px 0px 0px 0px;
        padding: 5px 0px 0px 10px;
        border-left: 1px #e4e4e4 solid;
    }
    </style>
    """,unsafe_allow_html=True)



#https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state
def check_rerun():
    print("check_rerun")
    if "rerun" not in st.session_state:
        st.session_state["rerun"] = False
    elif st.session_state["rerun"] == False:
        pass
    else:
        st.toast(body="Successfully submitted! ^_^", duration="short")
        st.session_state["rerun"] = False



fieldnames = ["date", "time", "entry", "entry_word_count", "summary"]
font_url="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:ital,wght@0,200..800;1,200..800&family=Courier+Prime:ital,wght@0,400;0,700;1,400;1,700&family=Crimson+Text:ital,wght@0,400;0,600;0,700;1,400;1,600;1,700&display=swap"
font_options = {
    "Sans Serif": {
        "name": "Atkinson Hyperlegible Next",
        "size": "16px",
        "index": 0
    },
    "Serif": {
        "name": "Crimson Text",
        "size": "16px",
        "index": 1
    },
    "Monospace": {
        "name": "Courier Prime",
        "size": "14px",
        "index": 2
    },
}



def check_font():
    print("check_font")
    if "font" in st.session_state:
        pass
    else:
        st.session_state["font"] = "Sans Serif"
    font = st.session_state["font"]
    html_str = f"""
    <style>
    @import url({font_url});
    p, textarea, dd, dt, div [data-baseweb="select"], div [data-testid="stTooltipHoverTarget"], div [data-testid="stFileUploaderDropzone"] {{
        font-family: {font_options[font]["name"]} !important;
        font-size: {font_options[font]["size"]} !important;
    }}
    div [data-testid="InputInstructions"] {{
        font-family: {font_options[font]["name"]} !important;
    }}
    </style>
    """
    st.markdown(html_str, unsafe_allow_html=True)



def get_words():
    print("get_words")
    count = 0
    try:
        with open("novel.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                count += int(row["entry_word_count"])
    except FileNotFoundError:
        pass
    if count == 0:
        count = "0 words." + "\n\n" + "(It's going to be great.)"
    elif count == 1:
        count = "1 word." + "\n\n" + "(And it's a great start.)"
    elif count > 1:
        count = f"{count} words." + "\n\n" + "(And they're all amazing.)"
    return count



def get_characters(entry):
    print("get_characters")
    chars = round(len(entry)/3)
    if chars < 50:
        chars = 50
    return chars




def date_parse(t):
    print("date_parse")
    matched_datetime = re.match(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}).*$", str(t))
    if matched_datetime:
        return matched_datetime.group(1), matched_datetime.group(2)
    else:
        raise ValueError("Error")



def date_format(d):
    print("date_format")
    date = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", d)
    if date:
        pass
    else:
        raise ValueError("Time is not in correct format")
    months = {
        "01": "January",
        "02": "February",
        "03": "March",
        "04": "April",
        "05": "May",
        "06": "June",
        "07": "July",
        "08": "August",
        "09": "September",
        "10": "October",
        "11": "November",
        "12": "December"
    }
    month = months[date.group(2)]
    day = date.group(3).lstrip("0")
    formatted_date = f"{month} {day}, {date.group(1)}"
    return formatted_date



def submit():
    print("submit")
    global fieldnames
    entry = st.session_state["novel_exe"]
    entry_word_count = len(entry.split(" "))
    summary = st.session_state["summary_exe"]
    date, time = date_parse(datetime.now())
    if os.path.exists("novel.csv") == False:
        with open("novel.csv", "a") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writerow({"date": "date", "time": "time", "entry": "entry", "entry_word_count": "entry_word_count", "summary": "summary"})
            writer.writerow({"date": date, "time": time, "entry": entry, "entry_word_count": entry_word_count, "summary": summary})
    else:
        with open("novel.csv", "a") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writerow({"date": date, "time": time, "entry": entry, "entry_word_count": entry_word_count, "summary": summary})
    st.session_state["novel_exe"] = ""
    st.session_state["rerun"] = True




@st.dialog(title="Add Summary", width="medium")
def dialog_submit():
    print("dialog_submit")
    st.write("Jot down some notes for future reference. (Or not – that's okay, too!) The character limit is determined by the length of your entry.")
    st.text_area(label="summary_exe",
                 height=None,
                 max_chars=get_characters(st.session_state["novel_exe"]),
                 key="summary_exe",
                 label_visibility="collapsed",
                 width="stretch")
    if st.button(label="Submit", key="submit", type="secondary", width="content"):
        submit()
        st.rerun()



#https://nicedouble-streamlitantdcomponentsdemo-app-middmy.streamlit.app/
@st.dialog(title="Summary", width="medium")
def dialog_summary():
    print("dialog_summary")
    summary = []
    try:
        with open("novel.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["summary"] == "":
                    summary.append(f'<dt>{date_format(row["date"])}</dt><dd><i>No summary submitted.</i></dd>')
                else:
                    summary.append(f'<dt>{date_format(row["date"])}</dt><dd><p>{row["summary"]}</p></dd>')
    except FileNotFoundError:
        summary = "A summary of your novel will go here!"
    separator = ""
    my_string = separator.join(sorted(summary, reverse=True))
    st.markdown(f"""<dl>{my_string}</dl>""",unsafe_allow_html=True)




@st.dialog(title="Export Work", width="small")
def dialog_export():
    print("dialog_export")
    st.download_button(label="Export Text", data=export_text(), file_name="novel.txt", mime="text/plain", type="secondary", width="content")
    with open("novel.csv", "r") as file:
        st.download_button(label="Export Raw Data", data=file, file_name="novel.csv", mime="text/csv", type="secondary", width="content")



def export_text():
    print("export_text")
    novel = ""
    with open("novel.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
                novel += row["entry"] + "\n\n"
    with open("novel.txt", "w") as file:
        file.write(novel)
    return novel



@st.dialog(title="Import Work", width="small")
def dialog_import():
    print("dialog_import")
    imported_file = st.file_uploader(label="Import Work",
                                    type=["txt", "csv"],
                                    accept_multiple_files=False,
                                    key=st.session_state["file_importer_key"],
                                    help=None,
                                    label_visibility="collapsed",
                                    width="stretch")
    if imported_file is not None:
        _, file_extension = os.path.splitext(imported_file.name)
        if file_extension == ".txt":
            if st.button(label="Save & Keep Working", key="save_text", type="secondary", width="content"):
                st.session_state["novel_exe"] = imported_file.read()
                st.session_state["file_importer_key"] += 1
                st.rerun()
        elif file_extension == ".csv":
            if st.button(label="Save & Close", key="save_csv", type="secondary", width="content"):
                import_csv(imported_file)



#https://discuss.streamlit.io/t/when-opening-an-uploaded-csv-file-expected-str-bytes-or-os-pathlike-object-not-uploadedfile/92150
def import_csv(file):

    print("import_csv")

    global fieldnames
    imported_csv = csv.DictReader(io.TextIOWrapper(file, encoding="utf-8"))

    if imported_csv.fieldnames is None:
        print("error")
        st.error("CSV file is not in a valid format.")
    elif imported_csv.fieldnames != fieldnames:
        print("error 2")
        st.error("CSV file is not in a valid format.")
    else:
        print("the fieldnames are: ", imported_csv.fieldnames)
        with open("novel.csv", "a") as newfile:
            writer = csv.DictWriter(newfile, fieldnames=fieldnames)
            writer.writerow({"date": "date", "time": "time", "entry": "entry", "entry_word_count": "entry_word_count", "summary": "summary"})
            for row in imported_csv:
                writer.writerow(row)
        st.session_state["file_importer_key"] += 1
        st.session_state["novel_exe"] = ""
        st.session_state["rerun"] = True
        st.rerun()



#https://discuss.streamlit.io/t/custom-fonts-on-streamlit/25984/11
#https://discuss.streamlit.io/t/passing-variable-containing-text-to-markdown/16069
@st.dialog(title="Settings", width="small", dismissible=False)
def dialog_settings():
    print("dialog_settings")
    font = st.selectbox("Select a font", font_options, key="font_selector", index=font_options[st.session_state["font"]]["index"])
    st.session_state["font"] = font
    check_font()
    if st.button(label="Save & Close", key="save_settings", type="secondary", width="content"):
        st.rerun()



def sidebar():
    print("sidebar")
    st.write(f"<div style='line-height: 1.25;'><p style='margin-bottom: 0px;'>You've submitted {get_words()}</p></div>",unsafe_allow_html=True)

    if st.button(label="Submit & Clear Text Area", key="dialog_submit", width="stretch"):
        if st.session_state["novel_exe"]:
            dialog_submit()
        else:
            st.toast(body="You have to write something first! :P", duration="short")

    if "novel_exe" in st.session_state:
        help = "Importing another file will overwrite the current entry. Continue?"
    else:
        help = None

    if os.path.exists("novel.csv") == False:
        if st.button(label="Import Work", key="dialog_import", width="stretch", help=help):
            if "file_importer_key" not in st.session_state:
                st.session_state["file_importer_key"] = 0
            else:
                st.session_state["file_importer_key"] += 1
            dialog_import()

    else:
        if st.button(label="View Summary", key="dialog_summary", width="stretch"):
            dialog_summary()
        if st.button(label="Export Work", key="dialog_export", width="stretch"):
            dialog_export()

    if st.button(label="Settings", key="dialog_settings", width="stretch"):
        dialog_settings()



def main():

    print("main")
    check_rerun()
    check_font()

    with st.sidebar:
        sidebar()

    st.text_area(label="novel_exe", label_visibility="collapsed", key="novel_exe", height=560, placeholder="It was a dark and stormy night...",)

    #https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeunload_event
    components.html("""<script>
        window.parent.document.querySelectorAll('textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            window.addEventListener('beforeunload', function (e) {
                e.preventDefault();
                e.returnValue = '';
            });
        }, { once: true } );
        });
        </script>
    """, height=0, width=0)



if __name__ == "__main__":
    main()
