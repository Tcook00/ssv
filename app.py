import re
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

def analyze_search_and_seizure(report_text):
    """
    Analyzes a police report for search and seizure compliance based on Arizona law.
    Flags missing probable cause and exceptions to the warrant requirement.
    """
    
    # Define key legal justifications for searches
    legal_bases = {
        "warrant": r"\b(warrant|judge-approved search)\b",
        "consent": r"\b(consent|agreed to search)\b",
        "plain_view": r"\b(plain view|object in sight)\b",
        "incident_to_arrest": r"\b(search incident to arrest|after arrest)\b",
        "exigent_circumstances": r"\b(exigent circumstances|emergency situation)\b",
        "automobile_exception": r"\b(vehicle search|car search|automobile exception)\b",
        "stop_and_frisk": r"\b(pat down|frisk|Terry stop)\b"
    }
    
    probable_cause_terms = r"\b(probable cause|reasonable suspicion|observed illegal activity|direct evidence)\b"
    
    # Check which legal bases are present in the report
    findings = {key: bool(re.search(pattern, report_text, re.IGNORECASE)) for key, pattern in legal_bases.items()}
    probable_cause_found = bool(re.search(probable_cause_terms, report_text, re.IGNORECASE))
    
    # Determine if the report includes a legal justification
    if not any(findings.values()):
        return "ALERT: No legal justification for search mentioned in the report. Possible unlawful search."
    
    # Check for probable cause when required
    if (findings["warrant"] or findings["automobile_exception"] or findings["incident_to_arrest"]) and not probable_cause_found:
        return "ALERT: No mention of probable cause for the search. Ensure probable cause is clearly stated."
    
    # Provide feedback on what was found
    valid_justifications = [key.replace('_', ' ').title() for key, found in findings.items() if found]
    return f"Search appears justified based on: {', '.join(valid_justifications)}. Ensure all necessary details, including probable cause, are included."

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        report_text = request.form['report_text']
        result = analyze_search_and_seizure(report_text)
    return render_template('index.html', result=result)

@app.route('/validate', methods=['POST'])
def validate_report():
    data = request.json
    report_text = data.get("report_text", "")
    result = analyze_search_and_seizure(report_text)
    return jsonify({"validation_result": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
