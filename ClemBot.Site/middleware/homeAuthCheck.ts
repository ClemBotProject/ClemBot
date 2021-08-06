import { Middleware } from '@nuxt/types'

const HomeAuthCheck: Middleware = async ({ app: { $auth } }) => {
  if (!$auth.loggedIn) {
    return
  }

  if ($auth.loggedIn && $auth.strategy.name === 'local') {
    debugger
  }

  if ($auth.loggedIn && $auth.strategy.name === 'discord') {
    //await $auth.loginWith('local')
  }
}

export default HomeAuthCheck
