import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Box, VStack, Text } from "@chakra-ui/react"
import { YentaChatService } from "../client"
import { useMemo } from "react"
import { createFileRoute } from "@tanstack/react-router"
import { useColorModeValue } from "@/components/ui/color-mode"
import type { YentaChatInfo, YentaChatMessage } from "../client/types.gen"
import { ChatInterface } from "../components/Chat/ChatInterface"

export const Route = createFileRoute('/chat')({
  component: ChatPage,
})

function ChatPage() {
  const queryClient = useQueryClient()
  const chatId = new URLSearchParams(window.location.search).get('chatId') ?? undefined;

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
    },
  })

  // Colors
  const textColor = useColorModeValue("gray.800", "white")
  const sidebarActiveBg = useColorModeValue("gray.100", "gray.700")

  // Handle chat selection
  const selectChat = (id: string) => {
    const params = new URLSearchParams(window.location.search)
    params.set("chatId", id)
    window.history.replaceState({}, '', `${window.location.pathname}?${params}`)
  }

  // Sidebar content
  const sidebar = (
    <>
      <Text fontSize="xl" fontWeight="bold" color={textColor} mb={4}>
        Chats
      </Text>
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
    </>
  )

  return (
    <ChatInterface
      messages={chatHistory?.messages || []}
      onSendMessage={(msg) => sendMessageMutation.mutate(msg)}
      isSending={sendMessageMutation.isPending}
      title="Chat with Yenta"
      sidebar={sidebar}
    />
  )
} 