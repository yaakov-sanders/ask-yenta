import { Button, Flex, Text, Textarea } from "@chakra-ui/react"
import { useCallback, useMemo, useState } from "react"

const TextBubble = ({ text }: { text: string }) => {
  return <Text>{text}</Text>
}
export const YentaChat = () => {
  const [text, setText] = useState("")
  const [conversation, setConversation] = useState<string[]>(["first message"])
  const appendToConversation = useCallback(
    (newText: string) => {
      setConversation((prevState) => [...prevState, newText])
    },
    [setConversation],
  )
  const conversationBubbles = useMemo(
    () => conversation.map((t) => <TextBubble text={t} />),
    [conversation],
  )
  const sendText = useCallback(() => {
    appendToConversation(text)
    setText("")
  }, [text, setText, appendToConversation])
  return (
    <Flex gap={4} direction={"column"}>
      {conversationBubbles}
      <Textarea value={text} onChange={(e) => setText(e.target.value)} />
      <Button onClick={sendText} disabled={!text} />
    </Flex>
  )
}
