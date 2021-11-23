export interface Guild {
  id: string
  name: string
  icon: string
  owner: boolean
  permissions: number
  features: string[]
  claims: string[]
  isAdded: boolean
  isHovered: boolean
}