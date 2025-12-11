# theme/chat_components.py

CHAT_BOX_STYLE = """
<style>
.chat-window {
    position: fixed;
    bottom: 100px;
    right: 20px;
    width: 350px;
    height: 480px;
    background: white;
    border-radius: 15px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.25);
    padding: 10px;
    z-index: 99999;
    display: flex;
    flex-direction: column;
}
.chat-header {
    font-weight: 700;
    color: #2D7FF9;
    font-size: 18px;
    margin-bottom: 5px;
}
.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
}
.chat-input {
    margin-top: 10px;
}
.chat-bubble-user {
    background: #66748a;
    padding: 8px 12px;
    border-radius: 12px;
    margin-bottom: 6px;
    align-self: flex-end;
}
.chat-bubble-ai {
    background: #2D7FF9;
    color: white;
    padding: 8px 12px;
    border-radius: 12px;
    margin-bottom: 6px;
    align-self: flex-start;
}
</style>
"""

def chat_popup_container():
    return """
    <div class="chat-window">
        <div class="chat-header">🤖 Mr. Finn</div>
        <div id="chat-messages" class="chat-messages"></div>
    </div>
    """
