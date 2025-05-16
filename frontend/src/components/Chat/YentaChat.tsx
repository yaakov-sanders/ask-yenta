import { Flex, Text, Textarea, VStack, HStack, Spinner, Box } from "@chakra-ui/react"
import { useMutation, useQuery } from "@tanstack/react-query"
import type React from "react"
import { useCallback, useEffect, useMemo, useState } from "react"

import { type ChatResponse, ChatService, type ChatHistoryResponse } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import { UsersService } from "@/client/sdk.gen"
import { Button } from "@/components/ui/button"
import { handleError } from "@/utils"

const TextBubble = ({ role, content }: { role: string; content: string }) => {
  // Colors optimized for dark mode
  const isUser = role === "user"
  
  return (
    <Box 
      bg={isUser ? "rgba(59, 130, 246, 0.3)" : "rgba(16, 185, 129, 0.3)"}
      p={3}
      borderRadius="lg"
      boxShadow="sm"
      alignSelf={isUser ? "flex-end" : "flex-start"}
      maxW="80%"
      borderWidth="1px"
      borderColor={isUser ? "blue.500" : "green.500"}
      mb={2}
    >
      <Text color="#FFFFFF" fontWeight="medium">
        {content}
      </Text>
    </Box>
  )
}

interface Message {
  role: string
  content: string
}

export const YentaChat = () => {
  const [text, setText] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [userId, setUserId] = useState<string>("")
  const [page, setPage] = useState(0)
  const limit = 10

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

  // Fetch chat history when userId is available
  const chatHistoryQuery = useQuery<ChatHistoryResponse>({
    queryKey: ["chatHistory", userId, page, limit],
    queryFn: () => ChatService.getChatHistory(userId, limit, page * limit),
    enabled: !!userId,
  })

  // Update messages when chat history changes
  useEffect(() => {
    if (chatHistoryQuery.data) {
      // Clear messages if this is the first page (page 0)
      if (page === 0) {
        setMessages(chatHistoryQuery.data.messages)
      } else {
        // Append older messages
        setMessages((prev) => [...chatHistoryQuery.data.messages, ...prev])
      }
    }
  }, [chatHistoryQuery.data, page])

  const appendMessage = useCallback(
    (newMessage: Message) => {
      setMessages((prevState) => [...prevState, newMessage])
    },
    [setMessages],
  )

  const chatMutation = useMutation<ChatResponse, ApiError, string>({
    mutationFn: (message: string) =>
      ChatService.chatWithMemory({ user_id: userId, message }),
    onSuccess: (data) => {
      appendMessage({ role: "assistant", content: data.reply })
    },
    onError: (err) => {
      appendMessage({
        role: "assistant",
        content: "Sorry, I'm having trouble connecting to my brain right now.",
      })
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

    // Add user message
    appendMessage({ role: "user", content: text })

    // Send the message to the chat API
    chatMutation.mutate(text)

    // Clear the input
    setText("")
  }, [text, setText, appendMessage, chatMutation, isDisabled])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        sendText()
      }
    },
    [sendText],
  )

  const loadMoreMessages = useCallback(() => {
    setPage((prevPage) => prevPage + 1)
  }, [])

  const hasMore = chatHistoryQuery.data?.has_more || false

  return (
    <Flex gap={4} direction="column" h="100%">
      {hasMore && (
        <Button 
          onClick={loadMoreMessages} 
          loading={chatHistoryQuery.isLoading} 
          size="sm"
          colorScheme="blue"
          variant="outline"
        >
          Load More
        </Button>
      )}
      
      {chatHistoryQuery.isLoading && page === 0 ? (
        <Flex justify="center" my={4}>
          <Spinner />
        </Flex>
      ) : (
        <VStack align="stretch" flex="1" overflowY="auto">
          {messages.map((msg, idx) => (
            <TextBubble key={idx} role={msg.role} content={msg.content} />
          ))}
        </VStack>
      )}
      
      <HStack mt="auto">
        <Textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={userId ? "Type your message to Yenta..." : "Loading..."}
          borderColor="gray.600"
          _hover={{ borderColor: "gray.500" }}
          _focus={{ borderColor: "blue.400" }}
          bg="gray.800"
          color="white"
        />
        <Button
          onClick={sendText}
          loading={chatMutation.isPending}
          disabled={isDisabled}
          colorScheme="blue"
        >
          Send
        </Button>
      </HStack>
    </Flex>
  )
}
