/* prettier-ignore-start */

/* eslint-disable */

// @ts-nocheck

// noinspection JSUnusedGlobalSymbols

// This file is auto-generated by TanStack Router

// Import Routes

import { Route as rootRoute } from './routes/__root'
import { Route as UserChatImport } from './routes/user-chat'
import { Route as SignupImport } from './routes/signup'
import { Route as ResetPasswordImport } from './routes/reset-password'
import { Route as RecoverPasswordImport } from './routes/recover-password'
import { Route as LoginImport } from './routes/login'
import { Route as ConnectionsImport } from './routes/connections'
import { Route as ChatImport } from './routes/chat'
import { Route as LayoutImport } from './routes/_layout'

// Create/Update Routes

const UserChatRoute = UserChatImport.update({
  path: '/user-chat',
  getParentRoute: () => rootRoute,
} as any)

const SignupRoute = SignupImport.update({
  path: '/signup',
  getParentRoute: () => rootRoute,
} as any)

const ResetPasswordRoute = ResetPasswordImport.update({
  path: '/reset-password',
  getParentRoute: () => rootRoute,
} as any)

const RecoverPasswordRoute = RecoverPasswordImport.update({
  path: '/recover-password',
  getParentRoute: () => rootRoute,
} as any)

const LoginRoute = LoginImport.update({
  path: '/login',
  getParentRoute: () => rootRoute,
} as any)

const ConnectionsRoute = ConnectionsImport.update({
  path: '/connections',
  getParentRoute: () => rootRoute,
} as any)

const ChatRoute = ChatImport.update({
  path: '/chat',
  getParentRoute: () => rootRoute,
} as any)

const LayoutRoute = LayoutImport.update({
  id: '/_layout',
  getParentRoute: () => rootRoute,
} as any)

// Populate the FileRoutesByPath interface

declare module '@tanstack/react-router' {
  interface FileRoutesByPath {
    '/_layout': {
      preLoaderRoute: typeof LayoutImport
      parentRoute: typeof rootRoute
    }
    '/chat': {
      preLoaderRoute: typeof ChatImport
      parentRoute: typeof rootRoute
    }
    '/connections': {
      preLoaderRoute: typeof ConnectionsImport
      parentRoute: typeof rootRoute
    }
    '/login': {
      preLoaderRoute: typeof LoginImport
      parentRoute: typeof rootRoute
    }
    '/recover-password': {
      preLoaderRoute: typeof RecoverPasswordImport
      parentRoute: typeof rootRoute
    }
    '/reset-password': {
      preLoaderRoute: typeof ResetPasswordImport
      parentRoute: typeof rootRoute
    }
    '/signup': {
      preLoaderRoute: typeof SignupImport
      parentRoute: typeof rootRoute
    }
    '/user-chat': {
      preLoaderRoute: typeof UserChatImport
      parentRoute: typeof rootRoute
    }
  }
}

// Create and export the route tree

export const routeTree = rootRoute.addChildren([
  LayoutRoute,
  ChatRoute,
  ConnectionsRoute,
  LoginRoute,
  RecoverPasswordRoute,
  ResetPasswordRoute,
  SignupRoute,
  UserChatRoute,
])

/* prettier-ignore-end */
