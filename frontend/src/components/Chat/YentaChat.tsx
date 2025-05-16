import { Button, Flex, Text, Textarea } from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import type React from "react"
import { useCallback, useEffect, useMemo, useState } from "react"

import { type ChatResponse, ChatService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import { UsersService } from "@/client/sdk.gen"
import { handleError } from "@/utils"

const TextBubble = ({ text }: { text: string }) => {
  return <Text>{text}</Text>
}

export const YentaChat = () => {
  const [text, setText] = useState("")
  const [conversation, setConversation] = useState<string[]>([])
  const [userId, setUserId] = useState<string>("")

  // Fetch the current user id on component mount
  useEffect(() => {
    const fetchUserId = async () => {
      try {
        const user = await UsersService.readUserMe()
        if (user?.id) {
          setUserId(String(user.id))
        }
      } catch (error) {
        console.error("Failed to fetch user:", error)
      }
    }

    fetchUserId()
  }, [])

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

  const chatMutation = useMutation<ChatResponse, ApiError, string>({
    mutationFn: (message: string) =>
      ChatService.chatWithMemory({ user_id: userId, message }),
    onSuccess: (data) => {
      appendToConversation(`Yenta: ${data.reply}`)
    },
    onError: (err) => {
      appendToConversation(
        "Yenta: Sorry, I'm having trouble connecting to my brain right now.",
      )
      handleError(err)
    },
  })

  const isDisabled = useMemo(
    () => !text || chatMutation.isPending || !userId,
    [text, chatMutation.isPending, userId],
  )

  const sendText = useCallback(() => {
    // Return early if no text, already loading, or no user ID
    if (isDisabled) return

    // Add user message to conversation
    appendToConversation(`You: ${text}`)

    // Send the message to the chat API
    chatMutation.mutate(text)

    // Clear the input
    setText("")
  }, [text, setText, appendToConversation, chatMutation, isDisabled])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        sendText()
      }
    },
    [sendText],
  )

  return (
    <Flex gap={4} direction={"column"}>
      {conversationBubbles}
      <Textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={userId ? "Type your message to Yenta..." : "Loading..."}
      />
      <Button
        onClick={sendText}
        loadingText="Sending..."
        loading={chatMutation.isPending}
        disabled={isDisabled}
      >
        Send
      </Button>
    </Flex>
  )
}
