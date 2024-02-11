<!-- Activity feed -->
<template>
    <aside class="bg-black/10 lg:fixed lg:bottom-0 lg:right-0 lg:top-0 lg:w-96 lg:overflow-y-auto lg:border-l lg:border-white/5">
        <header class="flex items-center justify-between border-b border-white/5 px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
            <h2 class="text-base font-semibold leading-7 text-white">Activity feed</h2>
            <!-- router-link to="#" class="text-sm font-semibold leading-6 text-indigo-400">View all</router-link> -->
        </header>
        <ul role="list" class="divide-y divide-white/5">
            <li v-for="line in logs" :key="line" class="px-4">
                <p :class="[logColor(line), 'truncate text-sm']">{{ displayLogText(line) }}</p>
            </li>
        </ul>
    </aside>
</template>


<script lang="ts">
import { ref } from 'vue'
import flaskApi from '@/router/api'

export default {
    name: 'DashboardView',

    data() {
        const logs: any = [];
        return {
            logs,
            sidebarOpen: ref(false),
        }
    },
    methods: {
        logColor(line: string) {
            let color: string = '';
            if (line.includes('RESPONSE')) {
                return 'text-green-500'
            }
            if (line.includes('SEND')) {
                return 'text-yellow-500'
            }
            return color
        },
        displayLogText(line: string) {
            if (line.includes('RESPONSE')) {
                return 'RESPONSE: ' + line
            }
            if (line.includes('SEND')) {
                return 'SEND: ' + line
            }
            return line.substring(0, 100)
        },
        async getActivity() {
            return await flaskApi.get('/activity')
        },
    },
    async mounted() {
        const logs = await this.getActivity()
        this.logs = logs
    }
}
</script>