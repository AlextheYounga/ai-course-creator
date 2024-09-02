<template>
    <form>
        <p class="font-bold text-xl">Question: {{ this.interactive.data.question }}</p>
        <template v-for="choice of choices">
            <input :class="`${choice.correct}`" type="radio" :id="`choice-${choice.id}`" name="radio">
            <label :class="`${choice.correct}`" :for="`choice-${choice.id}`">{{ `${choice.letter}.  ${choice.content}` }}</label>
        </template>
    </form>
</template>

<script>
export default {
    name: 'MultipleChoice',
    props: {
        interactive: {
            type: Object,
            required: true,
        }
    },
    computed: {
        choices() {
			const letters = 'abcdefghijklmnopqrstuvwxyz'
			const correctAnswer = this.interactive.data.answer
			let choicesList = []
            if (typeof this.interactive.data.content == 'string') {
                choicesList = this.interactive.data.content.split(',')
            } else {
				choicesList = this.interactive.data.content
			}

			return choicesList.map((choice, index) => {
				return { 
					id: `${this.interactive.id}-${index}`,
					letter: letters[index].toUpperCase(),
					correct: choice.trim() == correctAnswer ? 'correct' : 'incorrect',
					content: choice.trim(),
				}
			}) 
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
    text-align: right;
    padding-right: .5em;
	align-content: space-evenly;
    position: absolute;
    top: 0;
    bottom: 0;
    left: -100%;
    right: 100%;
    border-radius: .2em;
    z-index: -1;
    transition-property: left, right, color;
    transition-duration: 300ms;
}

/* Correct */
label.correct:after {
    content: " ✔";
    background-color: #98ECA3;
    color: #98ECA3;
}

input.correct:checked+label.correct {
    color: #48AC53
}

input.correct:checked+label.correct:after {
    left: 0;
    right: 0;
    color: #48AC53;
}

/* Incorrect */
label.incorrect:after {
    content: " ✖️";
    background-color: #ff5733;
    color: #ff5733;
}

input.incorrect:checked+label.incorrect {
    color: #ee4521
}

input.incorrect:checked+label.incorrect:after {
    left: 0;
    right: 0;
    color: #ee4521;
}
</style>