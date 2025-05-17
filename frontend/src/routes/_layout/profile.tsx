import {
  Box,
  Button as ChakraButton,
  Flex,
  Heading,
  Input,
  Stack,
  Text,
  Textarea,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useEffect, useState } from "react"
import { FiPlus, FiTrash2 } from "react-icons/fi"

import {
  ApiError,
  UserLLMProfileSummary,
  UserProfileResponse,
  UserProfileService,
  type UserPublic,
  UsersService,
} from "@/client"
import { Button } from "@/components/ui/button"
import { useColorModeValue } from "@/components/ui/color-mode"
import { Field } from "@/components/ui/field"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/_layout/profile")({
  component: ProfilePage,
})

function ProfilePage() {
  const [profileText, setProfileText] = useState("")
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  // Get the current user from the query cache - this is guaranteed to be loaded
  // in the parent Layout component
  const { data: currentUser, isLoading: isLoadingUser } = useQuery<UserPublic>({
    queryKey: ["currentUser"],
    queryFn: () => UsersService.readUserMe(),
  })

  // Color mode values
  const boxBg = useColorModeValue("white", "gray.800")
  const boxBorderColor = useColorModeValue("gray.200", "gray.700")
  const emptyBoxBg = useColorModeValue("gray.50", "gray.900")

  // Define the query function separately to handle error catching
  const fetchUserProfile = async (userId: string) => {
    try {
      return await UserProfileService.getUserProfile({ userId })
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        // Return empty data for 404 errors
        return { profile_summary: "" }
      }
      showErrorToast("We couldn't load your profile. Please try again.")
      throw error
    }
  }

  // Fetch user profile with React Query
  const { data, isLoading } = useQuery({
    queryKey: ["userProfile", currentUser?.id],
    queryFn: () => {
      if (!currentUser?.id) return Promise.resolve({ profile_summary: "" })
      return fetchUserProfile(currentUser.id)
    },
    enabled: !!currentUser?.id,
  })

  const profileSummary = data?.profile_summary || ""
  const hasProfile = profileSummary !== ""

  // Submit profile text mutation
  const submitProfileMutation = useMutation({
    mutationFn: (text: string) => {
      const method = hasProfile ? 'updateProfileFromText' : 'createProfileFromText'
      return UserProfileService[method]({
        userId: currentUser?.id || "",
        requestBody: { text },
      })
    },
    onSuccess: (response) => {
      queryClient.invalidateQueries({
        queryKey: ["userProfile", currentUser?.id],
      })
      setProfileText("")
      const status = (response as UserProfileResponse).status
      showSuccessToast(`Your profile was successfully ${status}.`)
    },
    onError: () => {
      showErrorToast("We couldn't update your profile. Please try again.")
    },
  })

  const handleSubmitProfile = () => {
    if (!currentUser?.id || !profileText.trim()) return
    submitProfileMutation.mutate(profileText)
  }

  const isPageLoading = isLoadingUser || isLoading

  return (
    <Box maxW="800px" mx="auto" py={6}>
      <Heading mb={6}>My Profile</Heading>

      {isPageLoading ? (
        <Box
          mb={8}
          p={4}
          borderWidth="1px"
          borderRadius="md"
          bg={emptyBoxBg}
          borderColor={boxBorderColor}
        >
          <Text>Loading your profile...</Text>
        </Box>
      ) : hasProfile ? (
        <Box
          mb={8}
          p={4}
          borderWidth="1px"
          borderRadius="md"
          bg={boxBg}
          borderColor={boxBorderColor}
          boxShadow="sm"
        >
          <Heading size="md" mb={4}>
            Your Profile Summary
          </Heading>
          <Box whiteSpace="pre-wrap">
            <Text>{profileSummary}</Text>
          </Box>
        </Box>
      ) : (
        <Box
          mb={8}
          p={4}
          borderWidth="1px"
          borderRadius="md"
          bg={emptyBoxBg}
          borderColor={boxBorderColor}
          boxShadow="sm"
        >
          <Text>
            You don't have a profile yet. Use the form below to create one.
          </Text>
        </Box>
      )}

      <Box my={6} borderBottomWidth="1px" borderColor={boxBorderColor} />

      <Stack gap={4}>
        <Heading size="md">
          {hasProfile ? "Update Your Profile" : "Create Your Profile"}
        </Heading>
        <Text>
          {hasProfile
            ? "Tell us about yourself. Our AI will update your profile based on your description."
            : "Tell us about yourself. This information will be used to personalize your experience."}
        </Text>
        <Textarea
          value={profileText}
          onChange={(e) => setProfileText(e.target.value)}
          placeholder="Describe yourself here..."
          rows={6}
          bg={boxBg}
          borderColor={boxBorderColor}
        />
        <Button
          loading={submitProfileMutation.isPending}
          onClick={handleSubmitProfile}
          colorScheme="blue"
          alignSelf="flex-start"
        >
          Submit
        </Button>
      </Stack>
    </Box>
  )
}

export default ProfilePage
