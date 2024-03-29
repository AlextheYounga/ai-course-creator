<template>
    <p class="text-lg">{{ this.data.description }}</p>
    <div class="codepen">
        <pre>
            <code :class="`language-${getTemplate().language}`">
                    {{ getTemplate().code }}
            </code>
        </pre>

        <pre>
            <code :class="`language-${getStyles().language}`">
                    {{ getStyles().code }}
            </code>
        </pre>

        <pre>
            <code :class="`language-${getScripts().language}`">
                    {{ getScripts().code }}
            </code>
        </pre>
    </div>
    <!-- <script async src="https://static.codepen.io/assets/embed/ei.js"></script> -->
</template>

<script>
export default {
    name: 'Codepen',
    props: {
        data: {
            type: Object,
            required: true,
        }
    },
    methods: {
        getTemplate() {
            return this.data.content.template
        },
        getStyles() {
            return this.data.content.styles
        },
        getScripts() {
            return this.data.content.scripts
        },
        language(language) {
            return `language-${language}`
        }
    },
};
</script>