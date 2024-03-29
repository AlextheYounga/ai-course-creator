<template>
    <form>
        <p class="font-bold text-xl">Question: {{ this.data.question }}</p>
        <template v-for="choice of choices">
            <input type="radio" :id="`choice-${uniqueId(choice)}`" name="radio">
            <label :for="`choice-${uniqueId(choice)}`">{{ `${getLetter(choice)}.  ${choice}` }}</label>
        </template>
    </form>
</template>

<script>
export default {
    name: 'MultipleChoice',
    props: {
        data: {
            type: Object,
            required: true,
        }
    },
    methods: {
        uniqueId(str) {
            // Deterministic hash from string
            var hash = 0, i, chr;
            if (str.length === 0) return hash;
            for (i = 0; i < str.length; i++) {
                chr   = str.charCodeAt(i);
                hash  = ((hash << 5) - hash) + chr;
                hash |= 0; // Convert to 32bit integer
            }
            return hash;
        },
        getLetter(choice) {
            const letters = 'abcdefghijklmnopqrstuvwxyz'
            const choiceIndex = this.choices.indexOf(choice)
            return letters[choiceIndex].toUpperCase()
        }
    },
    computed: {
        choices() {
            if (typeof this.data.content == 'string') {
                return this.data.content.split(',')
            }

            return this.data.content
        }
    }
};
</script>

<style scoped>
input {
    display: none;
}

label {
    display: block;
    font-family: sans-serif;
    color: #334155;
    font-weight: bold;
    font-size: 1.4em;
    line-height: 1.5em;
    margin: .5em;
    padding: 0.2em 1.5em;
    border-radius: .2em;
    position: relative;
    overflow: hidden;
    transition: color 500ms;
    cursor: pointer;
}

label:before {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #cbd5e1;
    z-index: -2;
}

label:after {
    content: " ✔";
    text-align: right;
    padding-right: .5em;
    position: absolute;
    top: 0;
    bottom: 0;
    left: -100%;
    right: 100%;
    border-radius: .2em;
    background-color: #98ECA3;
    color: #98ECA3;
    z-index: -1;
    transition-property: left, right, color;
    transition-duration: 300ms;
}

input:checked+label {
    color: #48AC53
}

input:checked+label:after {
    left: 0;
    right: 0;
    color: #48AC53;
}
</style>