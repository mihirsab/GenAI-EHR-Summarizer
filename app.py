from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import PyPDF2
import openai
import io

app = Flask(__name__)
openai.organization = "org-yhpBYmp8lcRMUF3tFWXQX1ac"
openai.api_key = "SECRET"
app.secret_key = 'your_secret_key'  # Change this to a random secret key
MAX_LENGTH = 3000

#Assuming we already connected other company's data into the system
Reports = ["This medical report summary provides a comprehensive overview of the health of the patient, Jane. The comprehensive metabolic panel results were within the normal range, suggesting normal kidney and liver function, electrolyte balance and glucose metabolism. In addition, a chest X-ray was performed and no abnormalities were observed. For lipid levels, the results were healthy and indicated good cardiovascular health. Furthermore, a bone density scan and complete blood count showed that there were no indications of osteoporosis and anemia respectively. Therefore, overall the patient is in good health with lifestyle counseling recommended to maintain a healthy lifestyle. ",
           "Jane suffers from several conditions, including hypertension, asthma, depression, and mild osteoarthritis in her shoulders and health. She takes various medications to control her conditions as well as nonsteroidal anti-inflammatory drugs (NSAIDs) for pain relief. She also follows a heart-healthy diet and regularly exercises at least thrice a week. Jane is current on her vaccinations and up-to-date on her preventive care visits. Overall, Jane is in good health and experiences minimal symptoms  ",
           "No further treatment was needed. Jane has received medical care from a variety of issues, including severe migraines, mild upper respiratory infection, and a routine check-up. Medications have been adjusted, referrals to specialists have been made, and general health advice has been provided during these visits. Through physical examinations all findings have been within normal limits. No further treatments have been considered at this time. "]



@app.before_request
def default_user_type():
    # Set default user type if not already set
    if 'user_type' not in session:
        session['user_type'] = 'patient'

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
    print(parts)
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
    return render_template('abc.html')  # This should contain the form for uploading PDF
@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    user_type = session['user_type']  # Default to 'patient' if not provided
    prompt_base = "Provide a concise medical summary, outlining overall health status, underlying health conditions, prescribed medications, and lifestyle management in plain language, with a maximum of 150 words"
    if user_type == 'doctor':
        prompt_base = "Generate a concise medical test summary, designed for doctors, encompassing all diseases and corresponding prescriptions within a 200-word limit."
    
    # Assuming extract_text_from_pdf and generate_summary are defined and return the expected values.
    if file:
        try:
            # Extract text from PDF
            text = extract_text_from_pdf(file)
            
            # Generate summary based on user type
            summary = generate_summary(text, prompt_base)
            
            # Return the result as JSON
            return jsonify({'summary': summary})
        except Exception as e:
            # Handle exceptions that could occur during PDF extraction and summary generation
            return jsonify({'error': str(e)}), 500

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
    return render_template('page2.html')

@app.route('/filter_upload', methods=['POST'])
def filter_upload():
    if 'filter_type' not in request.form:
        return jsonify({'error': 'Filter type not provided'}), 400

    filter_type = request.form.get('filter_type', '1')  # Default to '1' if not provided

    # Maps for prompt bases
    prompt_bases = {
        "1": "Generate a comprehensive lab test report summary for healthcare professionals in 200 words, including relevant diagnoses and recommended treatments.",
        "2": "Generate a concise medical history report summary, not exceeding 200 words, outlining all relevant medical conditions and associated prescriptions for healthcare professionals.",
        "3": "Generate a succinct clinical visit summary for healthcare professionals, providing essential details of the patient's visit, diagnosis, and treatment within a 200-word limit"
    }

    # Select the prompt base
    prompt_base = prompt_bases.get(filter_type, prompt_bases["1"])

    try:
        # Here you should define how Reports is retrieved or constructed before this line.
        # It might be coming from a database or an API, or even the user's input.
        # For this example, let's assume Reports is already defined and is a list of report strings.
        summary = ""
        while summary == "":
            text = ' '.join(Reports)
            
            # Generate summary based on filter type
            # print("Text to summarize:", text)  # This will help verify the text is correct before summarization
            summary = generate_summary(text, prompt_base)
            # print("Generated summary:", summary)  # This can help check if the summary is empty after the function call

        # text = ' '.join(Reports)
        
        # # Generate summary based on filter type
        # # print("Text to summarize:", text)  # This will help verify the text is correct before summarization
        # summary = generate_summary(text, prompt_base)
        # # print("Generated summary:", summary)  # This can help check if the summary is empty after the function call
        # # Return the summary as JSON
        
        return jsonify({'summary': summary})
    except Exception as e:
        # Handle exceptions that could occur during the summary generation
        return jsonify({'error': 'Failed to generate summary: {}'.format(str(e))}), 500
    
@app.route('/filter_question', methods=['POST'])
def filter_question():

    filter_question = request.form.get('filter_question')  # Default to '1' if not provided

    # Maps for prompt bases
    #prompt_bases = [filter_question]

    # Select the prompt base
    prompt_base = filter_question

    try:
        # Here you should define how Reports is retrieved or constructed before this line.
        # It might be coming from a database or an API, or even the user's input.
        # For this example, let's assume Reports is already defined and is a list of report strings.
  
            
        summary = "This report summarizes Jane's health status and confirms that she is healthy and in good condition. Her lipid levels are healthy and overall her lab results have been within the normal range. In addition, her medical conditions are managed well with medications and lifestyle modifications. Jane is current on all her preventive care visits and vaccinations and no further treatments were indicated. Therefore, Jane's overall health can be considered satisfactory."
            # print("Generated summary:", summary)  # This can help check if the summary is empty after the function call


        
        return jsonify({'summary': summary})
    except Exception as e:
        # Handle exceptions that could occur during the summary generation
        return jsonify({'error': 'Failed to generate summary: {}'.format(str(e))}), 500
@app.route('/set_user_type', methods=['POST'])
def set_user_type():
    user_type = request.form['user_type']
    session['user_type'] = user_type
    return redirect(url_for('index'))


@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')
if __name__ == '__main__':
    app.run(debug=True)
