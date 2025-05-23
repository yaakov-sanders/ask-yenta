import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Box, VStack, HStack, Input, Button, Text, Flex } from "@chakra-ui/react"
import { YentaChatService } from "../client"
import { useState, useMemo } from "react"
import { createFileRoute, useSearch } from "@tanstack/react-router"
import { useColorModeValue } from "@/components/ui/color-mode"
import type { YentaChatInfo, YentaMessage } from "../client/types.gen"

export const Route = createFileRoute('/chat')({
  component: ChatPage,
})

function ChatPage() {
  const queryClient = useQueryClient()
  const chatId = new URLSearchParams(window.location.search).get('chatId') ?? undefined;
  const [message, setMessage] = useState("")

  // Get all chats for sidebar
  const { data: chats } = useQuery({
    queryKey: ["chats"],
    queryFn: YentaChatService.getChats,
  })

  // Create new chat
  const createChatMutation = useMutation({
    mutationFn: YentaChatService.createChat,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chats"] })
    },
  })

  // Find selected chat info
  const selectedChat = useMemo(() =>
    chats?.chats_info.find((c) => c.conversation_id === chatId),
    [chats, chatId]
  )

  // Fetch messages for selected chat
  const { data: chatHistory } = useQuery({
    queryKey: ["chatHistory", chatId],
    queryFn: async () =>
      chatId ? await YentaChatService.getChatHistory({ chatConversationId: chatId }) : undefined,
    enabled: !!chatId,
  })

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (msg: string) =>
      YentaChatService.chatWithMemory({
        chatConversationId: chatId!,
        requestBody: { message: msg },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chatHistory", chatId] })
      setMessage("")
    },
  })

  // Colors
  const bgColor = useColorModeValue("white", "gray.800")
  const borderColor = useColorModeValue("gray.200", "gray.700")
  const textColor = useColorModeValue("gray.800", "white")
  const inputBg = useColorModeValue("gray.50", "gray.900")
  const sidebarBg = useColorModeValue("gray.50", "gray.900")
  const sidebarActiveBg = useColorModeValue("gray.100", "gray.700")

  // Handle chat selection
  const selectChat = (id: string) => {
    const params = new URLSearchParams(window.location.search)
    params.set("chatId", id)
    window.history.replaceState({}, '', `${window.location.pathname}?${params}`)
  }

  return (
    <Flex height="calc(100vh - 64px)">
      {/* Sidebar */}
      <Box w="260px" bg={sidebarBg} borderRight="1px" borderColor={borderColor} p={4}>
        <HStack justify="space-between" mb={4}>
          <Text fontSize="xl" fontWeight="bold" color={textColor}>
            Chats
          </Text>
          <Button
            colorScheme="blue"
            size="sm"
            onClick={() => createChatMutation.mutate()}
            loading={createChatMutation.isPending}
          >
            New
          </Button>
        </HStack>
        <VStack align="stretch" gap={1}>
          {chats?.chats_info.map((chat) => (
            <Box
              key={chat.conversation_id}
              px={3}
              py={2}
              borderRadius="md"
              bg={chat.conversation_id === chatId ? sidebarActiveBg : 'transparent'}
              cursor="pointer"
              color={textColor}
              fontWeight={chat.conversation_id === chatId ? "bold" : "normal"}
              onClick={() => selectChat(chat.conversation_id)}
              _hover={{ bg: sidebarActiveBg }}
            >
              {chat.name || chat.conversation_id}
            </Box>
          ))}
        </VStack>
      </Box>
      {/* Main chat area */}
      <Flex flex={1} direction="column" p={4} bg={bgColor}>
        <Text fontSize="2xl" fontWeight="bold" color={textColor} mb={4}>
          Chat with Yenta
        </Text>
        <Box mb={4} height="1px" bg={borderColor} />
        {chatId && chatHistory ? (
          <VStack gap={4} align="stretch" flex={1}>
            {chatHistory?.messages?.map((msg: YentaMessage, idx: number) => (
              <Box
                key={idx}
                p={2}
                bg={inputBg}
                borderRadius="md"
                alignSelf={msg.role === "user" ? "flex-end" : "flex-start"}
                color={textColor}
              >
                {msg.content}
              </Box>
            ))}
            <HStack mt={4}>
              <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your message..."
                bg={inputBg}
                color={textColor}
              />
              <Button
                colorScheme="blue"
                onClick={() => sendMessageMutation.mutate(message)}
                loading={sendMessageMutation.isPending}
                disabled={!message.trim()}
              >
                Send
              </Button>
            </HStack>
          </VStack>
        ) : (
          <Text color={textColor} mt={8} textAlign="center">
            Select a chat to start messaging.
          </Text>
        )}
      </Flex>
    </Flex>
  )
} 