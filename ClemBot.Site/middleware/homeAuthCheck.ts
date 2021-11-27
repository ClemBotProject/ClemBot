import { Middleware } from '@nuxt/types'

const HomeAuthCheck: Middleware = async ({ app: { $auth, $axios } }) => {
  if (!$auth.loggedIn) {
    return
  }

  if ($auth.loggedIn && $auth.strategy.name === 'local') {

  }

  if ($auth.loggedIn && $auth.strategy.name === 'discord') {
    await $auth.loginWith('local', {
      // @ts-ignore
      data: { bearer: $auth.strategy.token.get().split(' ')[1] },
    })
  }
}

export default HomeAuthCheck
