import { Middleware } from '@nuxt/types'

const DashboardAuthCheck: Middleware = async ({ app: { $auth }, redirect }) => {
  if (!$auth.loggedIn) {
      redirect('/')
  }
}

export default DashboardAuthCheck