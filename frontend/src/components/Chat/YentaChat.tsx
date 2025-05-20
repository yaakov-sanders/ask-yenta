import {
  Box,
  Flex,
  HStack,
  Spinner,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery } from "@tanstack/react-query"
import type React from "react"
import { useCallback, useEffect, useMemo, useState } from "react"

import type { ApiError } from "@/client/core/ApiError"
import {
  type ChatConversationInfo,
  type ChatGetChatHistoryResponse,
  type ChatMessageResponse,
  type ChatMessage
} from "@/client/types.gen"
import { ChatService, UsersService } from "@/client/sdk.gen"
import { Button } from "@/components/ui/button"
import { useColorModeValue } from "@/components/ui/color-mode"
import { handleError } from "@/utils"

const TextBubble = ({ messageType, content, role }: { messageType: string; content: string; role: string }) => {
  // Colors optimized for dark mode and light mode
  const isUser = role === "user"
  
  const userBubbleBg = useColorModeValue("blue.50", "rgba(59, 130, 246, 0.3)")
  const assistantBubbleBg = useColorModeValue("green.50", "rgba(16, 185, 129, 0.3)")
  const userBubbleBorder = useColorModeValue("blue.200", "blue.500")
  const assistantBubbleBorder = useColorModeValue("green.200", "green.500")
  const textColor = useColorModeValue("gray.800", "white")

  return (
    <Box
      bg={isUser ? userBubbleBg : assistantBubbleBg}
      p={3}
      borderRadius="lg"
      boxShadow="sm"
      alignSelf={isUser ? "flex-end" : "flex-start"}
      maxW="80%"
      borderWidth="1px"
      borderColor={isUser ? userBubbleBorder : assistantBubbleBorder}
      mb={2}
    >
      <Text color={textColor} fontWeight="medium">
        {content}
      </Text>
    </Box>
  )
}

export const YentaChat = () => {
  const [text, setText] = useState("")
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [selectedChatId, setSelectedChatId] = useState<string>("")
  const [lastMessageId, setLastMessageId] = useState<string | null>(null)
  const limit = 10
  
  // Define colors based on color mode
  const inputBg = useColorModeValue("white", "gray.800")
  const inputBorder = useColorModeValue("gray.200", "gray.600")
  const inputHoverBorder = useColorModeValue("gray.300", "gray.500")
  const inputFocusBorder = useColorModeValue("blue.300", "blue.400")
  const textColor = useColorModeValue("gray.800", "white")
  const selectBg = useColorModeValue("white", "#1A202C") // gray.800

  // Fetch the current user with React Query
  const userQuery = useQuery({
    queryKey: ["currentUser"],
    queryFn: UsersService.readUserMe,
  })

  const userId = useMemo(
    () => (userQuery.data?.id ? String(userQuery.data.id) : ""),
    [userQuery.data],
  )

  // Fetch available chats when userId is available
  const chatsQuery = useQuery({
    queryKey: ["chats", userId],
    queryFn: ChatService.getChats,
    enabled: !!userId,
  })

  // Create a new chat
  const createChatMutation = useMutation({
    mutationFn: ChatService.createChat,
    onSuccess: (data) => {
      setSelectedChatId(data.conversation_id)
    },
    onError: (err: Error) => {
      handleError(err as ApiError)
    },
  })

  // Fetch chat history when a chat is selected
  const chatHistoryQuery = useQuery<ChatGetChatHistoryResponse>({
    queryKey: ["chatHistory", selectedChatId, lastMessageId, limit],
    queryFn: () =>
      ChatService.getChatHistory({
        chatConversationId: selectedChatId,
        limit: limit,
        lastMessageId: lastMessageId,
      }),
    enabled: !!selectedChatId,
  })

  // Set the first chat as selected when chats are loaded and no chat is selected
  useEffect(() => {
    if (
      chatsQuery.data?.conversations_info.length &&
      !selectedChatId &&
      !createChatMutation.isPending
    ) {
      setSelectedChatId(chatsQuery.data.conversations_info[0].conversation_id)
    }
  }, [chatsQuery.data, selectedChatId, createChatMutation.isPending])

  // Update messages when chat history changes
  useEffect(() => {
    if (chatHistoryQuery.data) {
      setMessages(chatHistoryQuery.data.messages)
    }
  }, [chatHistoryQuery.data])

  const appendMessage = useCallback(
    (newMessage: ChatMessage) => {
      setMessages((prevState) => [...prevState, newMessage])
    },
    [setMessages],
  )

  const chatMutation = useMutation<ChatMessageResponse, ApiError, string>({
    mutationFn: (message: string) =>
      ChatService.chatWithMemory({
        chatConversationId: selectedChatId,
        requestBody: {
          message: message,
        },
      }),
    onSuccess: (data) => {
      // The latest message is the response
      if (data.messages.length > 0) {
        appendMessage(data.messages[data.messages.length - 1])
      }
    },
    onError: (err) => {
      appendMessage({
        content: "Sorry, I'm having trouble connecting to my brain right now.",
        message_type: "assistant",
        role: "yenta"
      })
      handleError(err)
    },
  })

  const isDisabled = useMemo(
    () => !text || chatMutation.isPending || !selectedChatId || userQuery.isLoading,
    [text, chatMutation.isPending, selectedChatId, userQuery.isLoading],
  )

  const sendText = useCallback(() => {
    // Return early if no text, already loading, or no chat selected
    if (isDisabled) return

    // Add user message to the UI immediately
    appendMessage({
      content: text,
      message_type: "human",
      role: "user"
    })

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

  const createNewChat = useCallback(() => {
    createChatMutation.mutate()
  }, [createChatMutation])

  const loadMoreMessages = useCallback(() => {
    if (messages.length > 0) {
      // Get the oldest message to fetch history before it
      // Using content as a simple way to identify the message since id isn't available
      const oldestMessageContent = messages[0].content
      setLastMessageId(oldestMessageContent)
    }
  }, [messages])

  // Correct the has_more property check
  const hasMoreMessages = useMemo(() => {
    // This is a safe check since ChatHistoryResponse doesn't have has_more property
    return messages.length >= limit; // Assume there might be more if we got a full page
  }, [messages, limit]);

  return (
    <Flex gap={4} direction="column" h="100%">
      <HStack>
        <Box flex="1">
          <select
            value={selectedChatId}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelectedChatId(e.target.value)}
            disabled={chatsQuery.isLoading}
            style={{
              backgroundColor: selectBg,
              color: textColor,
              borderColor: inputBorder,
              borderWidth: "1px",
              borderRadius: "0.375rem",
              padding: "0.5rem",
              width: "100%",
            }}
          >
            <option value="" disabled>Select a chat</option>
            {chatsQuery.data?.conversations_info.map((chat: ChatConversationInfo) => (
              <option key={chat.conversation_id} value={chat.conversation_id}>
                {chat.name || `Chat ${chat.conversation_id.slice(0, 8)}`}
              </option>
            ))}
          </select>
        </Box>
        <Button
          onClick={createNewChat}
          loading={createChatMutation.isPending}
          colorScheme="blue"
          variant="outline"
        >
          New Chat
        </Button>
      </HStack>

      {hasMoreMessages && (
        <Button
          onClick={loadMoreMessages}
          loading={chatHistoryQuery.isLoading && !!lastMessageId}
          size="sm"
          colorScheme="blue"
          variant="outline"
        >
          Load More
        </Button>
      )}

      {chatHistoryQuery.isLoading && !lastMessageId ? (
        <Flex justify="center" my={4}>
          <Spinner />
        </Flex>
      ) : (
        <VStack align="stretch" flex="1" overflowY="auto">
          {messages.map((msg, idx) => (
            <TextBubble key={idx} messageType={msg.message_type} content={msg.content} role={msg.role} />
          ))}
        </VStack>
      )}

      <HStack mt="auto">
        <Textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            userQuery.isLoading
              ? "Loading..."
              : !selectedChatId
              ? "Select or create a chat..."
              : "Type your message to Yenta..."
          }
          borderColor={inputBorder}
          _hover={{ borderColor: inputHoverBorder }}
          _focus={{ borderColor: inputFocusBorder }}
          bg={inputBg}
          color={textColor}
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
