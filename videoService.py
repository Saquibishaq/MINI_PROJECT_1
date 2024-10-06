import sys
import requests
from gtts import gTTS
from transformers import pipeline
from moviepy.editor import *
import spacy
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

nlp = spacy.load("en_core_web_sm")

PIXABAY_API_KEY = "45901871-577ac26a62f94274074f7578a"  # Replace with your actual Pixabay API key

# Fetch images from Pixabay
def fetch_images(query, index, num_images=10):
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&image_type=photo&per_page={num_images}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4XX, 5XX)
        
        response_json = response.json()
        image_paths = []
        
        if 'hits' in response_json and len(response_json['hits']) > 0:
            for i, hit in enumerate(response_json['hits']):
                image_url = hit['largeImageURL']
                image_path = f'image_{index}_{i}.jpg'
                
                img_data = requests.get(image_url).content
                with open(image_path, 'wb') as handler:
                    handler.write(img_data)

                image_paths.append(image_path)
        else:
            print(f"No images found for query: {query}")

        return image_paths

    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return []

# Extract keywords using NLP
def extract_keywords(sentence):
    doc = nlp(sentence)
    return [token.text for token in doc if token.pos_ in ["NOUN", "VERB", "PROPN"]]

# Generate story from a prompt
def generate_story(prompt):
    story_generator = pipeline('text-generation', model='gpt2', device=0)  # Set device to 0 for GPU, or -1 for CPU
    story = story_generator(prompt, max_length=500, num_return_sequences=1, truncation=True)
    return story[0]['generated_text']

# Generate video from text
def generate_video_from_text(prompt):
    generated_story = generate_story(prompt)
    tts = gTTS(text=generated_story, lang='en')
    audio_file = "generated_story.mp3"
    tts.save(audio_file)
    
    sentences = generated_story.split('. ')
    image_paths_per_sentence = []

    for i, sentence in enumerate(sentences):
        keywords = extract_keywords(sentence)
        query = "+".join(keywords)
        image_paths = fetch_images(query, i, num_images=8)
        image_paths_per_sentence.append(image_paths)

    # Create video clips from images
    audio_clip = AudioFileClip(audio_file)

    # Limit the total video duration to 60 seconds (increased from 30 seconds)
    max_video_duration = 60
    sentence_duration = max_video_duration / len(sentences) if sentences else 1  # Avoid division by zero

    clips = []
    for i, sentence_images in enumerate(image_paths_per_sentence):
        if not sentence_images:  # Check if there are images for the current sentence
            print(f"No images found for sentence {i}: {sentences[i]}")
            continue  # Skip this iteration if no images are available

        sub_clips = []
        image_duration = sentence_duration / len(sentence_images)

        for image_path in sentence_images:
            image_clip = ImageClip(image_path).set_duration(image_duration)
            sub_clips.append(image_clip)

        if sub_clips:  # Only concatenate if there are sub_clips
            sentence_clip = concatenate_videoclips(sub_clips, method="compose")
            clips.append(sentence_clip)
        else:
            print(f"No valid image clips for sentence {i}")

    # Check if clips are empty before concatenating
    if not clips:
        print("No valid video clips created. Exiting video generation.")
        return None  # Or handle the error as needed

    # Concatenate all the sentence clips
    final_video = concatenate_videoclips(clips, method="compose").set_audio(audio_clip)
    final_video_file = "final_video.mp4"
    final_video.write_videofile(final_video_file, fps=24)  # Set the output file name and frame rate
    return final_video_file

if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else input("Enter a prompt: ")
    video_file = generate_video_from_text(prompt)
    if video_file:
        print(f"Video generated: {video_file}")
    else:
        print("Video generation failed.")
