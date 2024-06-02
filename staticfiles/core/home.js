const form = document.querySelector("#outfits-form");
const winnerInput = document.querySelector("#winner-input");

form.addEventListener("submit", event => {
  event.preventDefault();

  const winner = event.submitter.id === "outfit1-image" ? 1 : 2;
  winnerInput.value = document.querySelector(`#outfit${winner}-input`).value;

  form.submit();
})
