import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Box, VStack, Text } from "@chakra-ui/react"
import { UsersChatService, UsersService } from "../client"
import { useMemo } from "react"
import { createFileRoute } from "@tanstack/react-router"
import { useColorModeValue } from "@/components/ui/color-mode"
import type { UsersChatInfo, UsersChatMessage } from "../client/types.gen"
import { ChatInterface } from "../components/Chat/ChatInterface"

export const Route = createFileRoute('/user-chat')({
  component: UserChatPage,
})

function UserChatPage() {
  const queryClient = useQueryClient()
  const chatId = new URLSearchParams(window.location.search).get('chatId') ?? undefined;

  // Get current user
  const { data: currentUser } = useQuery({
    queryKey: ["currentUser"],
    queryFn: UsersService.readUserMe,
  })

  // Get all chats for sidebar
  const { data: chats } = useQuery({
    queryKey: ["userChats"],
    queryFn: UsersChatService.getChats,
  })

  // Find selected chat info
  const selectedChat = useMemo(() =>
    chats?.chats_info.find((c) => c.conversation_id === chatId),
    [chats, chatId]
  )

  // Get participant info
  const { data: participants } = useQuery({
    queryKey: ["chatParticipants", selectedChat?.participant_ids],
    queryFn: () => UsersService.readUsers(),
    enabled: !!selectedChat?.participant_ids,
  })

  // Map participant IDs to user info
  const participantMap = useMemo(() => {
    const map: Record<string, any> = {}
    participants?.data.forEach((u) => { map[u.id] = u })
    if (currentUser) map[currentUser.id] = currentUser
    return map
  }, [participants, currentUser])

  // Fetch messages for selected chat
  const { data: chatHistory } = useQuery({
    queryKey: ["userChatHistory", chatId],
    queryFn: async () =>
      chatId ? await UsersChatService.getChatHistory({ chatConversationId: chatId }) : undefined,
    enabled: !!chatId,
  })

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (msg: string) =>
      UsersChatService.chatWithMemory({
        chatConversationId: chatId!,
        requestBody: { message: msg },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["userChatHistory", chatId] })
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
        Conversations
      </Text>
      <VStack align="stretch" gap={1}>
        {chats?.chats_info.map((chat) => {
          const otherParticipantId = chat.participant_ids.find(id => id !== currentUser?.id)
          const otherParticipant = participantMap[otherParticipantId || '']
          return (
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
              {otherParticipant?.email || chat.conversation_id}
            </Box>
          )
        })}
      </VStack>
    </>
  )

  return (
    <ChatInterface
      messages={chatHistory?.messages || []}
      onSendMessage={(msg) => sendMessageMutation.mutate(msg)}
      isSending={sendMessageMutation.isPending}
      currentUserId={currentUser?.id}
      title={selectedChat ? `Chat with ${participantMap[selectedChat.participant_ids.find(id => id !== currentUser?.id) || '']?.email}` : undefined}
      sidebar={sidebar}
    />
  )
} 