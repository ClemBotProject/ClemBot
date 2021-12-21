<template>
  <div>
    <b-message
      class="mb-3"
      size="is-primary"
      type="is-primary-light"
      :closable="false"
      title="Tags"
    />
    <b-button
      v-if="canAddTag"
      class="has-text-white is-dark mx-1 my-2"
      @click="addTag = !addTag"
      icon-right="plus"
    >
      Create Tag
    </b-button>
    <div v-if="addTag" class="box has-background-dark">
      <div class="columns">
        <div class="column is-3">
          <b-field>
            <template #label>
              <span class="has-text-white">Name</span>
            </template>
            <b-input
              id="white-text"
              :maxlength="20"
              v-model="tagAddName"
            ></b-input>
          </b-field>
          <b-button
            v-if="tagAddContent != '' && tagAddName != ''"
            class="has-text-white is-primary mx-1 my-2 centered"
            @click="createTag"
            icon-right="plus"
          >
            Save Tag
          </b-button>
        </div>
        <div class="column">
          <b-field id="white-text" class="column has-text-white">
            <template #label>
              <span class="has-text-white">Content</span>
            </template>
            <b-input
              type="textarea"
              :maxlength="1000"
              v-model="tagAddContent"
            ></b-input>
          </b-field>
        </div>
      </div>
    </div>
    <div class="box">
      <tags-table :data="tags" />
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import dashboard from '~/layouts/dashboard.vue'
import TagsTable from '~/components/dashboard/TagsTable.vue'
import { Tag } from '~/services/api/routes/Tags'
import { BotAuthClaims } from '~/services/Claims'

export default Vue.extend({
  components: { dashboard, TagsTable },
  layout: 'dashboard',

  data() {
    let tags: Array<Tag> = []
    let addTag = false
    let tagAddName = ''
    let tagAddContent = ''

    return {
      tags,
      addTag,
      tagAddName,
      tagAddContent,
    }
  },

  computed: {
    canAddTag: function (): boolean{
      // @ts-ignore
      let guildId: string = this.$route.params.id
      // @ts-ignore
      let activeGuild = this.$auth.user?.guilds.filter(
        (x: { id: string }) => x.id == guildId
      )[0]
      return activeGuild.claims.find((x: string) => x === BotAuthClaims.tagAdd)
    },
  },

  async fetch() {
    let guildId = this.$route.params.id
    try {
      this.tags = (await this.$api.tags.getGuildTags(guildId)) ?? []
    }
    catch(e){
      this.tags = []
    }
  },

  methods: {
    async createTag() {
      // @ts-ignore
      let userId = this.$auth.user?.user.user.id
      let guildId: string = this.$route.params.id
      try {
        await this.$api.tags.createTag(
          this.tagAddName,
          this.tagAddContent,
          guildId,
          userId
        )
      } catch (x) {
        console.log(x)
      }
      this.addTag = false

      this.tags = (await this.$api.tags.getGuildTags(guildId)) ?? []
    },
  },
})
</script>

<style>
#white-text {
  color: white;
}
</style>
