from flask import Flask, request, render_template
import PyPDF2
import openai
import io

app = Flask(__name__)
openai.organization = "org-yhpBYmp8lcRMUF3tFWXQX1ac"
openai.api_key = "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"
MAX_LENGTH = 3000

#Assuming we already connected other company's data into the system
Reports = ["This medical report summary provides a comprehensive overview of the health of the patient, Jane. The comprehensive metabolic panel results were within the normal range, suggesting normal kidney and liver function, electrolyte balance and glucose metabolism. In addition, a chest X-ray was performed and no abnormalities were observed. For lipid levels, the results were healthy and indicated good cardiovascular health. Furthermore, a bone density scan and complete blood count showed that there were no indications of osteoporosis and anemia respectively. Therefore, overall the patient is in good health with lifestyle counseling recommended to maintain a healthy lifestyle. ",
           "Jane suffers from several conditions, including hypertension, asthma, depression, and mild osteoarthritis in her shoulders and health. She takes various medications to control her conditions as well as nonsteroidal anti-inflammatory drugs (NSAIDs) for pain relief. She also follows a heart-healthy diet and regularly exercises at least thrice a week. Jane is current on her vaccinations and up-to-date on her preventive care visits. Overall, Jane is in good health and experiences minimal symptoms  ",
           "No further treatment was needed. Jane has received medical care from a variety of issues, including severe migraines, mild upper respiratory infection, and a routine check-up. Medications have been adjusted, referrals to specialists have been made, and general health advice has been provided during these visits. Through physical examinations all findings have been within normal limits. No further treatments have been considered at this time. "]




def split_prompt(text, split_length):
    if split_length <= 0:
        raise ValueError("Max length must be greater than 0.")

    num_parts = (len(text) + split_length - 1) // split_length
    file_data = []

    for i in range(num_parts):
        start = i * split_length
        end = start + split_length
        part_text = text[start:end]
        file_data.append(part_text)

    return file_data

def generate_summary(text, prompt_base):    
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
    prompt_base = "Generate a medical summary in no more than 100 words in layman term:"
    if user_type == 'doctor':
        prompt_base = "Generate medical report summary in no more than 200 words with all diseases and prescriptions for doctors:"
    if file:
        # Extract text from PDF
        text = extract_text_from_pdf(file)
        
        # Generate summary based on user type
        summary_html = generate_summary(text, prompt_base)
        
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
@app.route('/filter', methods=['GET'])
def filter():
    # This will render the filter.html template when '/filter' is accessed via GET
    return render_template('filter.html')

@app.route('/filter_upload', methods=['POST'])
def filter_upload():
    filter_type = request.form.get('filter_type', '1')  # Default to 'patient' if not provided
    prompt_base = "Generate medical report summary in no more than 200 words with all diseases and prescriptions for doctors:"
    if filter_type == "1":
        prompt_base = "Generate medical test summary in no more than 200 words with all diseases and prescriptions for doctors: "
    elif filter_type =="2":
        prompt_base = "Generate medical history summary in no more than 200 words with all diseases and prescriptions for doctors:"
    elif filter_type == "3":
        prompt_base = "Generate clinical visits summary in no more than 200 words with all diseases and prescriptions for doctors:"

    text = ' '.join(Reports)
        
    # Generate summary based on user type
    summary_html = generate_summary(text, prompt_base)
        
    # Render the result
    return render_template('result.html', summary=summary_html)

@app.route('/hacksc', methods=['GET'])
def hacksc():
    return render_template('hacksc.html')
if __name__ == '__main__':
    app.run(debug=True)
