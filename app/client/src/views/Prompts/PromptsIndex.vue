
<template>
  <!-- Log Index -->
  <div class="container mx-auto">
    <div class="py-4">
      <Breadcrumbs />
    </div>
    
    <header class="flex items-center justify-between border-b border-white/5 px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
      <h1 class="text-base font-semibold leading-7 text-white">App Logs</h1>
    </header>
    <ul role="list" class="divide-y divide-white/5">
      <li v-for="line in logs" :key="line.prompt.id.toString()" class="relative flex items-center space-x-4 py-4">
        <div class="min-w-0 flex-auto">
          <div class="flex items-center gap-x-3">
            <h2 class="min-w-0 text-sm font-semibold leading-6 text-white">
              <router-link :to="`/prompts/${line.prompt.id}`" class="flex gap-x-2 cursor-pointer">
                <span class="text-cyan-500 truncate">Prompt</span>
                <span class="text-gray-400">/</span>
                <span class="whitespace-nowrap">{{ line.prompt.action }}</span>
                <span class="absolute inset-0" />
              </router-link>
            </h2>
          </div>
          <div class="mt-3 flex items-center gap-x-2.5 text-xs leading-5 text-gray-400">
            <p class="truncate">{{ line.response.created_at }}</p>
            <svg viewBox="0 0 2 2" class="h-0.5 w-0.5 flex-none fill-gray-300">
              <circle cx="1" cy="1" r="1" />
            </svg>
            <p class="whitespace-nowrap">{{ line.prompt.model }}</p>
          </div>
        </div>
        <div class="rounded-full flex-none py-1 px-2 text-xs font-medium ring-1 ring-inset">{{ line.response.total_tokens }} tokens</div>
        <div class="rounded-full flex-none py-1 px-2 text-xs font-medium ring-1 ring-inset">temperature: {{ line.prompt.properties?.temperature ?? 1 }}</div>
        <ChevronRightIcon class="h-5 w-5 flex-none text-gray-400" aria-hidden="true" />
      </li>
    </ul>
  </div>
</template>


<script>
import flaskApi from '@/router/api'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { EllipsisVerticalIcon } from '@heroicons/vue/20/solid'
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
  name: 'PromptsIndex',

  components: {
    Breadcrumbs,
    Dialog,
    DialogPanel,
    DialogTitle,
    Menu,
    MenuButton,
    MenuItem,
    MenuItems,
    TransitionChild,
    TransitionRoot,
    XMarkIcon,
    EllipsisVerticalIcon,
  },

  data() {
    const open = false
    const logs = [];
    const selectedLog = null;

    return {
      selectedLog,
      open,
      logs,
    }
  },

  methods: {
    selectLine(line) {
      this.selectedLog = line
      this.open = true
    },
  },

  async mounted() {
    const logs = await flaskApi.get('/prompts')
    this.logs = logs
  }
}
</script>