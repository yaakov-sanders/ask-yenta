import {useCallback, useMemo, useState} from 'react'

const TextBubble = ({text}: { text: string }) => {
    return <span>{text}</span>
}
export const YentaChat = () => {
    const [text, setText] = useState('')
    const [conversation, setConversation] = useState<string[]>(['first message'])
    const appendToConversation = useCallback((newText: string) => {
        setConversation((prevState) => [...prevState, newText])
    }, [setConversation])
    const conversationBubbles = useMemo(() => conversation.map(t => <TextBubble text={t}/>), [conversation])
    const sendText = useCallback(() => {
        appendToConversation(text);
        setText('')
    }, [text, setText, appendToConversation])
    return <div className="yenta-chat">
        {conversationBubbles}
        <textarea value={text} onChange={(e) => setText(e.target.value)}/>
        <button onClick={sendText}/>
    </div>
}