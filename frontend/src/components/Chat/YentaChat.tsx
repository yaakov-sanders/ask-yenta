import { Button, Flex, Text, Textarea } from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import React, { useCallback, useMemo, useState } from "react"

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

  const isDisabled = useMemo(() => !text || promptMutation.isPending, [text, promptMutation.isPending]);

  const sendText = useCallback(() => {
    // Return early if no text or already loading
    if (isDisabled) return;
    
    // Add user message to conversation
    appendToConversation(`You: ${text}`)
    
    // Send the prompt to the LLM
    promptMutation.mutate(text)
    
    // Clear the input
    setText("")
  }, [text, setText, appendToConversation, promptMutation, isDisabled])
  
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendText();
      }
    },
    [sendText]
  );
  
  return (
    <Flex gap={4} direction={"column"}>
      {conversationBubbles}
      <Textarea 
        value={text} 
        onChange={(e) => setText(e.target.value)} 
        onKeyDown={handleKeyDown}
      />
      <Button onClick={sendText} loading={promptMutation.isPending} disabled={isDisabled}>
        Send
      </Button>
    </Flex>
  )
}
