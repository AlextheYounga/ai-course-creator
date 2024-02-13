<template>
    <div class="container mx-auto">
        <div class="py-4">
            <Breadcrumbs />
        </div>

        <h1 class="text-2xl font-medium text-gray-200 pt-12">Topics</h1>
        <ul role="list" class="mt-3 grid grid-cols-1 gap-5 sm:grid-cols-2 sm:gap-6 lg:grid-cols-4 pt-6">
            <li v-for="topic in topicCards" :key="topic.name" class="col-span-1 flex rounded-md shadow-sm">
                <div :class="[topic.bgColor, 'flex w-16 flex-shrink-0 items-center justify-center rounded-l-md text-sm font-medium text-white']">{{ topic.initials }}</div>
                <div class="flex flex-1 items-center justify-between truncate rounded-r-md border-b border-r border-t border-gray-200 bg-white">
                    <div class="flex-1 truncate px-4 py-2 text-sm">
                        <a :href="topic.href" class="font-medium text-gray-900 hover:text-gray-600">{{ topic.name }}</a>
                        <p class="text-gray-500">{{ topic.outlineCount }} Outlines</p>
                    </div>
                    <!-- <div class="flex-shrink-0 pr-2">
                        <button type="button" class="inline-flex h-8 w-8 items-center justify-center rounded-full bg-transparent bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                            <span class="sr-only">Open options</span>
                            <EllipsisVerticalIcon class="h-5 w-5" aria-hidden="true" />
                        </button>
                    </div> -->
                </div>
            </li>
        </ul>
    </div>
</template>
  
<script lang="ts">
import flaskApi from '@/router/api'
import { EllipsisVerticalIcon } from '@heroicons/vue/20/solid'
import type { Topic } from '@/types/ModelTypes';
import Breadcrumbs from '@/components/Breadcrumbs.vue'

type TopicCard = {
    name: String
    initials: String
    href: String
    outlineCount: Number | undefined
    bgColor: String
}

export default {
    name: 'TopicsIndex',
    components: {
        EllipsisVerticalIcon,
        Breadcrumbs
    },
    data() {
        const topics: Topic[] = []
        const topicCards: any  = []
        return {
            topics,
            topicCards
        }
    },
    methods: {
        async getTopics() {
            const topics = await flaskApi.get('/topics') as Topic[]
            this.topics = topics

            this.translateToCards()
        },

        translateToCards() {
            this.topics.forEach((topic: Topic) => {
                const card = {
                    name: topic.name,
                    initials: topic.name.charAt(0),
                    href: `#`,
                    outlineCount: topic.outline_count,
                    bgColor: 'bg-red-600'
                }
                this.topicCards.push(card)
            })
        }
    },

    mounted() {
        this.getTopics()
    }
}
</script>


  
<!-- [
    { name: 'Graph API', initials: 'GA', href: '#', members: 16, bgColor: 'bg-pink-600' },
    { name: 'Component Design', initials: 'CD', href: '#', members: 12, bgColor: 'bg-purple-600' },
    { name: 'Templates', initials: 'T', href: '#', members: 16, bgColor: 'bg-yellow-500' },
    { name: 'React Components', initials: 'RC', href: '#', members: 8, bgColor: 'bg-green-500' },
] -->