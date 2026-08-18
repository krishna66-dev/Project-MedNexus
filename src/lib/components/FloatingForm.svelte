<script lang="ts">
	import "../styles/FloatingForm.scss";

	let email = "";
	let success = "";
	let loading = false;
	let done = false;
	let isActive = false;

	const submitFunc = async () => {
		loading = true;
		try {
			const res = await fetch(
				"https://ladybird-subscription.fly.dev/subscribe",
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({ email }),
				}
			);
			const data = await res.json();
			console.log(data);

			// if (data.success) {
			setTimeout(() => {
				loading = false;
				done = true;
			}, 1000);
			// }
		} catch (error) {
		} finally {
			setTimeout(() => {
				loading = false;
				done = false;
				email = "";
			}, 2000);
		}
	};

	const handleFocus = () => {
		isActive = true;
		try {
			navigator.vibrate(300);
		} catch (error) {
			console.log("error", error);
		}
	};

	const handleBlur = () => {
		if (email === "") {
			isActive = false;
		}
	};

	const handleSubmit = (e: Event) => {
		e.preventDefault();
		submitFunc();
	};
</script>

<form
	class="FloatingForm FloatingForm--{isActive ? 'active' : ''}"
	on:submit={handleSubmit}
>
	<label
		class="FloatingForm__label FloatingForm__label--{isActive ? 'active' : ''}"
		for="email-input"
	>
		Email or Phone number
	</label>
	<input
		id="email-input"
		type="email"
		name="email"
		placeholder="Enter your email here"
		bind:value={email}
		on:focus={handleFocus}
		on:blur={handleBlur}
	/>
	<button
		class="FloatingForm__button"
		type="button"
		on:click={submitFunc}
	>
		Join Us
	</button>
</form>
