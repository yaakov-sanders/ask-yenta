import { Outlet, createFileRoute } from "@tanstack/react-router"
import { Navigation } from "../components/Common/Navigation"

export const Route = createFileRoute('/__root')({
  component: Root,
})

function Root() {
  return (
    <>
      <Navigation />
      <Outlet />
    </>
  )
}
