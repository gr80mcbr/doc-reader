import openai
import os
from dotenv import load_dotenv

def main():
	load_dotenv()
	openai.api_key = os.getenv("OPENAI_API_KEY")
	training_response = openai.File.create(
	  file=open("training_data.jsonl", "rb"),
	  purpose='fine-tune'
	)

	training_file_id = training_response["id"]

	response = openai.FineTuningJob.create(
			training_file=training_file_id,
			model="gpt-3.5-turbo",
			suffix="lwfm_assistant"
	)

	job_id = response["id"]

	print(repsponse)

	response = openai.FineTuningJob.list_events(id=job_id, limit=50)

	events = response["data"]
	events.reverse()

	for event in events:
		print(event["message"])
