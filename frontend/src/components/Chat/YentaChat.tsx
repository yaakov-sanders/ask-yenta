import { Button, Flex, Text, Textarea } from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import { useCallback, useMemo, useState } from "react"

import type { ApiError } from "@/client/core/ApiError"
import { UserProfileService, type LLMResponse } from "@/client"
import { handleError } from "@/utils"

const TextBubble = ({ text }: { text: string }) => {
  return <Text>{text}</Text>
}

export const YentaChat = () => {
  const [text, setText] = useState("")
  const [conversation, setConversation] = useState<string[]>([])

  const appendToConversation = useCallback(
    (newText: string) => {
      setConversation((prevState) => [...prevState, newText])
    },
    [setConversation],
  )
  
  const conversationBubbles = useMemo(
    () => conversation.map((t, i) => <TextBubble key={i} text={t} />),
    [conversation],
  )

  const promptMutation = useMutation<LLMResponse, ApiError, string>({
    mutationFn: (prompt: string) => UserProfileService.sendPrompt({ prompt }),
    onSuccess: (data) => {
      appendToConversation(`Yenta: ${data.response}`)
    },
    onError: (err) => {
      appendToConversation("Yenta: Sorry, I'm having trouble connecting to my brain right now.")
      handleError(err)
    },
  })

  const sendText = useCallback(() => {
    // Add user message to conversation
    appendToConversation(`You: ${text}`)
    
    // Send the prompt to the LLM
    promptMutation.mutate(text)
    
    // Clear the input
    setText("")
  }, [text, setText, appendToConversation, promptMutation])
  
  return (
    <Flex gap={4} direction={"column"}>
      {conversationBubbles}
      <Textarea value={text} onChange={(e) => setText(e.target.value)} />
      <Button onClick={sendText} loading={promptMutation.isPending} disabled={!text || promptMutation.isPending}>
        Send
      </Button>
    </Flex>
  )
}
