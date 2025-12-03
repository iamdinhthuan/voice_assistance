from groq import Groq

class LLMService:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.system_prompt = """You are a helpful and friendly English language assistant. 
        Your goal is to help the user practice English conversation. 
        Keep your responses concise and natural. 
        Correct any major grammatical errors the user makes in a gentle way, but focus on keeping the conversation flowing.
        """
        self.history = [{"role": "system", "content": self.system_prompt}]

    def get_response(self, user_text: str) -> str:
        """
        Get response from Groq LLM.
        """
        self.history.append({"role": "user", "content": user_text})
        
        try:
            completion = self.client.chat.completions.create(
                model="openai/gpt-oss-20b", # Fast and good for chat
                messages=self.history,
                temperature=0.7,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            response_text = completion.choices[0].message.content
            self.history.append({"role": "assistant", "content": response_text})
            return response_text
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I'm sorry, I'm having trouble thinking right now."

    def clear_history(self):
        self.history = [{"role": "system", "content": self.system_prompt}]
