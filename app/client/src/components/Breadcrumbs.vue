<template>
  <nav class="flex" aria-label="Breadcrumb">
    <ol role="list" class="flex items-center space-x-4">
      <li>
        <div>
          <router-link to="/" class="text-gray-400 hover:text-gray-500">
            <HomeIcon class="h-5 w-5 flex-shrink-0" aria-hidden="true" />
            <span class="sr-only">Home</span>
          </router-link>
        </div>
      </li>
      <li v-for="page in pages" :key="page.name">
        <div v-if="page.current" class="flex items-center">
          <ChevronRightIcon class="h-5 w-5 flex-shrink-0 text-gray-300" aria-hidden="true" />
          <span class="ml-4 text-sm font-medium text-gray-300" :aria-current="page.current ? 'page' : undefined">{{ page.name }}</span>
        </div>
        <div v-else class="flex items-center">
          <ChevronRightIcon class="h-5 w-5 flex-shrink-0 text-gray-300" aria-hidden="true" />
          <router-link :to="page.href" class="ml-4 text-sm font-medium text-cyan-500 hover:text-cyan-700" :aria-current="page.current ? 'page' : undefined">{{ page.name }}</router-link>
        </div>
      </li>
    </ol>
  </nav>
</template>
  

<script lang="ts">
import { ChevronRightIcon, HomeIcon } from '@heroicons/vue/20/solid'
import { capitalize } from '@/assets/helpers'

export default {
  components: {
    HomeIcon,
    ChevronRightIcon
  },
  data() {
    const pages: any = undefined

    return {
      pages
    }
  },
  methods: {
    buildBreadcrumbs() {
      const route = this.$route
      const pathSlugs = route.path.split('/').filter((slug: string) => slug !== '')

      if (pathSlugs.length === 1) {
        return [{
          name: capitalize(route.name as string),
          href: route.path,
          current: true
        }]
      }

      let index = 0
      const pageObjects = []
      for (const slug of pathSlugs) {
        pageObjects.push({
          name: capitalize(slug),
          href: route.path.split('/').slice(0, index + 2).join('/'),
          current: index === pathSlugs.length - 1
        })

        index++
      }

      return pageObjects
    },
  },
  mounted() {
    this.pages = this.buildBreadcrumbs()
    console.log(this.pages)
  }
}
</script>