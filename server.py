from datetime import timedelta, datetime

from flask import Flask, request, jsonify
from supermemo2 import SMTwo

app = Flask(__name__)

@app.route('/')
def hello():
    # parse body. The json has such fields: easiness, interval, repetitions, answer
    return 'Hello, World!'


@app.route('/sm2', methods=['POST'])
def process_sm2():
    if request.method == 'POST':
        data = request.json
        result = None
        if data.get('easiness') is not None and data.get('interval') is not None and data.get('repetitions') is not None:
            # Assuming JSON contains fields: easiness, interval, repetitions, answer
            easiness = float(data.get('easiness'))
            interval = int(data.get('interval'))
            repetitions = int(data.get('repetitions'))
            answer = 3 if bool(data.get('correct')) is True else 0
            result = SMTwo(easiness, interval, repetitions).review(answer)
        else:
            answer = 3 if bool(data.get('correct')) is True else 0
            result = SMTwo.first_review(answer)
        current_time = datetime.now()
        next_review_date_time = datetime(current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second, current_time.microsecond)
        result.review_date = next_review_date_time
        return jsonify(result.__dict__)
    else:
        return jsonify({'status': 'error', 'message': 'Only POST requests are allowed'}), 405


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)