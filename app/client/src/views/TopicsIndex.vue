<template>
  <!-- Log Index -->
  <div class="container mx-auto">
    <div class="py-4">
      <Breadcrumbs />
    </div>

    <NewTopicModal :open="modalOpen" />

    <div class="mx-auto max-w-7xl">
      <div class="py-10">
        <div class="px-4 sm:px-6 lg:px-8">
          <div class="sm:flex sm:items-center">
            <div class="sm:flex-auto">
              <h1 class="text-base font-semibold leading-6 text-white">Topics</h1>
              <p class="mt-2 text-sm text-gray-300">A list of all topics</p>
            </div>
            <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
              <button @click="modalOpen = true" type="button"
                class="block rounded-md bg-indigo-500 px-3 py-2 text-center text-sm font-semibold text-white hover:bg-indigo-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500">
                Add Topic
              </button>
            </div>
          </div>
          <div class="mt-8 flow-root">
            <div class="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
              <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
                <table class="min-w-full divide-y divide-gray-700">
                  <thead>
                    <tr>
                      <th v-for="column in this.columns" :key="column.key" scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-white sm:pl-0">{{ column.name }}</th>
                      <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-0">
                        <span class="sr-only">Edit</span>
                      </th>
                      <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-0">
                        <span class="sr-only">Delete</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody v-if="this.topics.length" class="divide-y divide-gray-800">
                    <tr v-for="topic in topics" :key="topic.id">
                      <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-white sm:pl-0">{{ topic.name }}</td>
                      <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-300">{{ topic.outlines?.length }}</td>
                      <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-300">{{ topic.created_at }}</td>
                      <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-0">
                        <button @click="editTopic(topic)" class="text-indigo-400 hover:text-indigo-300">
                          <PencilSquareIcon class="h-6 w-6 text-white" aria-hidden="true" />
                        </button>
                      </td>
                      <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-0">
                        <button @click="destroyTopic(topic)" class="text-indigo-400 hover:text-indigo-300">
                          <TrashIcon class="h-6 w-6 text-white" aria-hidden="true" />
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import fastApi from '@/router/api'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import NewTopicModal from '../components/modals/NewTopicModal.vue'
import { PencilSquareIcon, TrashIcon } from '@heroicons/vue/24/outline';

export default {
  name: 'PromptIndex',
  components: {
    Breadcrumbs,
    NewTopicModal,
    PencilSquareIcon,
    TrashIcon
  },

  data() {
    const columns = [
      { name: 'Name', key: 'name' },
      { name: 'Outlines', key: 'outlines' },
      { name: 'Created At', key: 'created_at' },
    ]
    return {
      modalOpen: false,
      columns: columns,
      topics: []
    }
  },
  watch: {
    modalOpen: function (val) {
      this.getTopics()
    } 
  },
  methods: {
    async getTopics() {
      const res = await fastApi.get('/topics')
      this.$data.topics = res.data
    },
    editTopic(topic) {
      console.log(topic)
    },
    destroyTopic(topic) {
      fastApi.delete(`/topics/${topic.id}`).then(() => {
        this.getTopics()
      })
    }
  },
  mounted() {
    this.getTopics()
  },

}
</script>