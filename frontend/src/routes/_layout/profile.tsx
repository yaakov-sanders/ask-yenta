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
  UserLLMProfileRead,
  UserProfileService,
  type UserPublic,
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
  const [newProfileField, setNewProfileField] = useState({ key: "", value: "" })
  const [fieldsToUpdate, setFieldsToUpdate] = useState<Record<string, any>>({})
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  
  // Get the current user from the query cache - this is guaranteed to be loaded
  // in the parent Layout component
  const { data: currentUser, isLoading: isLoadingUser } = useQuery<UserPublic>({
    queryKey: ["currentUser"],
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
        return { profile_data: {} }
      }
      showErrorToast("We couldn't load your profile. Please try again.")
      throw error
    }
  }

  // Fetch user profile with React Query
  const { data, isLoading } = useQuery({
    queryKey: ["userProfile", currentUser?.id],
    queryFn: () => {
      if (!currentUser?.id) return Promise.resolve({ profile_data: {} })
      return fetchUserProfile(currentUser.id)
    },
    enabled: !!currentUser?.id,
  })

  const userProfile = data?.profile_data || {}

  // Submit profile text mutation
  const submitProfileMutation = useMutation({
    mutationFn: (text: string) => 
      UserProfileService.submitProfileText({
        userId: currentUser?.id || "",
        requestBody: { text },
      }),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ["userProfile", currentUser?.id] })
      setProfileText("")
      showSuccessToast(`Your profile was successfully ${response.status}.`)
    },
    onError: () => {
      showErrorToast("We couldn't update your profile. Please try again.")
    }
  })

  // Update profile fields mutation
  const updateProfileMutation = useMutation({
    mutationFn: (data: Record<string, any>) => 
      UserProfileService.updateUserProfile({
        userId: currentUser?.id || "",
        requestBody: { data },
      }),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ["userProfile", currentUser?.id] })
      setFieldsToUpdate({})
      showSuccessToast(`Your profile was successfully ${response.status}.`)
    },
    onError: () => {
      showErrorToast("We couldn't update your profile. Please try again.")
    }
  })

  const handleUpdateProfileField = (key: string, value: any) => {
    setFieldsToUpdate((prev) => ({
      ...prev,
      [key]: value,
    }))
  }

  const handleAddField = () => {
    if (newProfileField.key.trim() && newProfileField.value.trim()) {
      handleUpdateProfileField(newProfileField.key, newProfileField.value)
      setNewProfileField({ key: "", value: "" })
    }
  }

  const handleRemoveField = (key: string) => {
    handleUpdateProfileField(key, null)
  }

  const handleSubmitProfile = () => {
    if (!currentUser?.id || !profileText.trim()) return
    submitProfileMutation.mutate(profileText)
  }

  const handleUpdateProfile = () => {
    if (!currentUser?.id || Object.keys(fieldsToUpdate).length === 0) return
    updateProfileMutation.mutate(fieldsToUpdate)
  }

  const isPageLoading = isLoadingUser || isLoading

  return (
    <Box maxW="800px" mx="auto" py={6}>
      <Heading mb={6}>My Profile</Heading>
      
      {isPageLoading ? (
        <Box mb={8} p={4} borderWidth="1px" borderRadius="md" bg={emptyBoxBg} borderColor={boxBorderColor}>
          <Text>Loading your profile...</Text>
        </Box>
      ) : Object.keys(userProfile).length > 0 ? (
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
            Your Current Profile
          </Heading>
          <Box whiteSpace="pre-wrap">
            {Object.entries(userProfile).map(([key, value]) => (
              <Box key={key} mb={2}>
                <Text as="span" fontWeight="bold">
                  {key}:{" "}
                </Text>
                <Text as="span">
                  {typeof value === "object" ? JSON.stringify(value) : String(value)}
                </Text>
              </Box>
            ))}
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

      {!isPageLoading && Object.keys(userProfile).length > 0 && (
        <Box mb={8}>
          <Heading size="md" mb={4}>
            Edit Profile Fields
          </Heading>
          <Stack gap={4}>
            {Object.entries(userProfile).map(([key, value]) => (
              <Field key={key} label={key}>
                <Flex>
                  <Input
                    defaultValue={
                      typeof value === "object" ? JSON.stringify(value) : String(value)
                    }
                    onChange={(e) =>
                      handleUpdateProfileField(key, e.target.value)
                    }
                    flex="1"
                  />
                  <ChakraButton
                    aria-label="Remove field"
                    ml={2}
                    colorScheme="red"
                    variant="outline"
                    onClick={() => handleRemoveField(key)}
                  >
                    <FiTrash2 />
                  </ChakraButton>
                </Flex>
              </Field>
            ))}
            
            <Box my={2} borderBottomWidth="1px" borderColor={boxBorderColor} />
            
            <Flex>
              <Field mr={2} label="New Field">
                <Input 
                  placeholder="Field name"
                  value={newProfileField.key}
                  onChange={(e) =>
                    setNewProfileField((prev) => ({
                      ...prev,
                      key: e.target.value,
                    }))
                  }
                />
              </Field>
              <Field label="Value">
                <Input
                  placeholder="Field value"
                  value={newProfileField.value}
                  onChange={(e) =>
                    setNewProfileField((prev) => ({
                      ...prev,
                      value: e.target.value,
                    }))
                  }
                />
              </Field>
              <ChakraButton
                aria-label="Add field"
                mt="auto"
                ml={2}
                onClick={handleAddField}
              >
                <FiPlus />
              </ChakraButton>
            </Flex>
            
            <Button
              colorScheme="blue"
              loading={updateProfileMutation.isPending}
              onClick={handleUpdateProfile}
              alignSelf="flex-start"
              mt={2}
            >
              Update Profile
            </Button>
          </Stack>
        </Box>
      )}

      <Box my={6} borderBottomWidth="1px" borderColor={boxBorderColor} />

      <Stack gap={4}>
        <Heading size="md">
          {Object.keys(userProfile).length > 0 ? "Rewrite Your Profile" : "Create Your Profile"}
        </Heading>
        <Text>
          {Object.keys(userProfile).length > 0 
            ? "Alternatively, you can describe yourself in natural language and our AI will update your profile."
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
