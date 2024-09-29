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
        const response = await fetch('http://127.0.0.1:5000/start_conversation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ language_code: 'hi' }),
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        speechText.textContent = data.message;
        conversationStarted = true;
        playAssistantAudio(data.audio_url);

        // Wait for the audio to finish before starting recording
        document.getElementById('assistantAudio').onended = () => {
            startRecording();
        };
    } catch (error) {
        console.error('Error starting conversation:', error)
        speechText.textContent = `त्रुटि: ${error.message}। कृपया पुनः प्रयास करें।`;
    }
};


function playAssistantAudio(audioUrl) {
    const audioElement = document.getElementById('assistantAudio');
    audioElement.src = audioUrl;
    audioElement.onerror = (e) => {
        console.error('Error loading audio:', e);
        speechText.textContent = "ऑडियो लोड करने में त्रुटि। कृपया पुनः प्रयास करें।";
    };
    audioElement.play().catch(e => {
        console.error('Error playing audio:', e);
        speechText.textContent = "ऑडियो चलाने में त्रुटि। कृपया पुनः प्रयास करें।";
    });
}


const startRecording = async () => {
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
};

const sendAudioToBackend = async (audioBlob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'speech.wav');

    try {
        const response = await fetch('http://127.0.0.1:5000/process_audio', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.user_input && data.assistant_response) {
            speechText.textContent = `आपने कहा: "${data.user_input}"`;
            diagnosisResult.textContent = data.assistant_response;

            if (data.audio_url) {
                playAssistantAudio(data.audio_url);
            }

            // Check if the conversation should end
            if (data.conversation_ended) {
                conversationStarted = false;
                voiceButton.disabled = true;
                voiceButton.style.backgroundColor = '#bdc3c7';
            } else {
                // If conversation hasn't ended, wait for audio to finish before starting next recording
                document.getElementById('assistantAudio').onended = () => {
                    startRecording();
                };
            }
        } else {
            throw new Error('सर्वर से अमान्य प्रतिक्रिया');
        }
    } catch (error) {
        console.error('Error:', error);
        speechText.textContent = `त्रुटि: ${error.message}। कृपया पुनः प्रयास करें।`;
    }
};




voiceButton.addEventListener('click', async () => {
    if (!conversationStarted) {
        await startConversation();
    } else {
        startRecording();
    }
});

consultButton.addEventListener('click', () => {
    if (consultationStatus.textContent === 'Not Connected') {
        consultationStatus.textContent = 'Connected';
        consultationStatus.style.color = '#27ae60';
    } else {
        consultationStatus.textContent = 'Not Connected';
        consultationStatus.style.color = '';
    }
});