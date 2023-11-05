from flask import Flask, request, render_template
import PyPDF2
import openai
import io

app = Flask(__name__)
openai.organization = "org-yhpBYmp8lcRMUF3tFWXQX1ac"
openai.api_key = "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"
MAX_LENGTH = 3000
def split_prompt(text, split_length):
    if split_length <= 0:
        raise ValueError("Max length must be greater than 0.")

    num_parts = (len(text) + split_length - 1) // split_length
    file_data = []

    for i in range(num_parts):
        start = i * split_length
        end = start + split_length
        part_text = text[start:end]
        # message = "End of text." if i == num_parts - 1 else f"Continuing to part {i + 2}."
        # content = f"[START PART {i + 1}]\n{part_text}\n[END PART {i + 1}]\n{message}"
        file_data.append(part_text)

    return file_data

def generate_summary(text, user_type='patient'):
    # Determine the appropriate prompt based on user type
    prompt_base = "Generate a medical summary in no more than 100 words in layman term:"
    if user_type == 'doctor':
        prompt_base = "Generate medical report summary in no more than 200 words with all diseases and prescriptions for doctors:"
    
    # If text is short enough, directly return the summary
    if len(text) <= MAX_LENGTH:
        return summarize_text(text, prompt_base)
    
    # If text is too long, split and summarize each part
    parts = split_prompt(text, MAX_LENGTH)
    summaries = []
    summary = ""
    for part in parts:
        # part should be a dictionary with 'content' key
        summary = summarize_text(summary + part, prompt_base)
    
    return summary

# Helper function to perform the summarization
def summarize_text(text, prompt_base):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"{prompt_base}\n\n{text}",
        max_tokens=200  # Adjust as needed
    )
    summary = response.choices[0].text.strip()
    return summary

@app.route('/')
def index():
    return render_template('upload.html')  # This should contain the form for uploading PDF

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf' not in request.files:
        return 'No file part'

    file = request.files['pdf']
    if file.filename == '':
        return 'No selected file'

    user_type = request.form.get('user_type', 'patient')  # Default to 'patient' if not provided

    if file:
        # Extract text from PDF
        text = extract_text_from_pdf(file)
        
        # Generate summary based on user type
        summary_html = generate_summary(text, user_type=user_type)
        
        # Render the result
        return render_template('result.html', summary=summary_html)

def extract_text_from_pdf(file):
    # Create a PDF file reader object
    pdfReader = PyPDF2.PdfReader(file)

    # Initialize a variable to store all the text
    all_text = ""

    # Iterate over all the pages
    for page in pdfReader.pages:
        # Extract text from the page and add it to the all_text variable
        text = page.extract_text()
        if text:  # Making sure there's text on the page
            all_text += text

    # Return the extracted text
    return all_text


if __name__ == '__main__':
    app.run(debug=True)
