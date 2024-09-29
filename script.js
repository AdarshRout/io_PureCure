const voiceButton = document.getElementById('voiceButton');
const diagnosisResult = document.getElementById('diagnosisResult');
const speechText = document.getElementById('speechText');
const consultButton = document.querySelector('.consult-button');
const consultationStatus = document.getElementById('consultationStatus');

let mediaRecorder;
let audioChunks = [];
let conversationStarted = false;

const startConversation = async () => {
    try {
        const response = await fetch('http://localhost:5000/start_conversation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ language_code: 'hi' }), // Hindi language code
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        speechText.textContent = data.message;
        conversationStarted = true;
    } catch (error) {
        console.error('Error starting conversation:', error);
        speechText.textContent = `Error: ${error.message}. Please try again.`;
    }
};

const sendAudioToBackend = async (audioBlob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'speech.wav');

    try {
        const response = await fetch('http://localhost:5000/process_audio', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.user_input && data.assistant_response) {
            speechText.textContent = `You said: "${data.user_input}"`;
            diagnosisResult.textContent = data.assistant_response;

            // Check if the conversation should end
            if (data.conversation_ended) {
                conversationStarted = false;
                voiceButton.disabled = true;
                voiceButton.style.backgroundColor = '#bdc3c7';
            }
        } else {
            throw new Error('Invalid response from server');
        }
    } catch (error) {
        console.error('Error:', error);
        speechText.textContent = `Error: ${error.message}. Please try again.`;
    }
};

voiceButton.addEventListener('click', async () => {
    if (!conversationStarted) {
        await startConversation();
        return;
    }

    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            mediaRecorder.start();
            speechText.textContent = 'Recording...';
            voiceButton.style.backgroundColor = '#e74c3c'; // Change button color while recording

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                voiceButton.style.backgroundColor = ''; // Reset button color
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                sendAudioToBackend(audioBlob);
            };

            setTimeout(() => {
                mediaRecorder.stop();
                speechText.textContent = 'Processing...';
            }, 5000);

        } catch (error) {
            console.error('Error accessing microphone:', error);
            speechText.textContent = `Error accessing microphone: ${error.message}`;
        }
    }
});

consultButton.addEventListener('click', () => {
    // Here you would typically implement the logic to start a consultation
    // For this example, we'll just toggle the status
    if (consultationStatus.textContent === 'Not Connected') {
        consultationStatus.textContent = 'Connected';
        consultationStatus.style.color = '#27ae60';
    } else {
        consultationStatus.textContent = 'Not Connected';
        consultationStatus.style.color = '';
    }
});