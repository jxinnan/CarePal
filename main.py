import gradio as gr
from utils.MedicalChatbot import MedicalChatbot

first_time = True

# Main application loop
def main():
    # Initialize the chatbot
    chatbot = MedicalChatbot()


    # chat function for gradio
    def gradio_chat(message, history):
        global first_time
        if first_time:
            first_time = False
            chatbot.select_avatar(message)
            return "Now chatting with your chosen avatar"
        return chatbot.chat(message)
  

    chat_block = gr.ChatInterface(
        fn=gradio_chat,
        examples=["Diabetes", "Depression", "Osteoporosis"], # TODO: select dynamically from database
        example_labels=["Mr. David Tan - Diabetes", "Mdm. Lim Siew Lan - Depression", "Mdm. Lim Mei Hui - Osteoporosis"],
        type="messages"
    ).launch()

if __name__ == "__main__":
    main()
