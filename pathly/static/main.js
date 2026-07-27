addEventListener("DOMContentLoaded", (event) => {
  
  const uploadForm = document.getElementById("kml-upload-form");
  const addSpecButton = document.getElementById("add-spec-button");
  const specForm = document.getElementById("spec_form");

  if (uploadForm) {
  uploadForm.addEventListener("submit", uploadKml)
  }

  if (addSpecButton) {
  addSpecButton.addEventListener("click", addSpecification)
  }

  if (specForm) {
    document.getElementById("spec_form").addEventListener("submit", handleSpecifications)
    
    const specificationContainers = document.querySelectorAll(".specifications_container");
    specificationContainers.forEach(function(container) {
      setupSpecificationContainer(container);
    });
  }    
});


async function uploadKml(event) {
  event.preventDefault();

  const fileInput = document.getElementById("file-upload");
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  const formData = new FormData();
  formData.append("kml_file", fileInput.files[0]);

  const response = await fetch(`/handle_kml`, {
    method: "POST",
    body: formData,
    headers: {
      "X-CSRFToken": csrftoken
    }
  });
  const data = await response.json();
  }

function addSpecification(event) {
  event.preventDefault();
  const specificationsContainer = document.getElementById("spec_parent_container");
  const originalSpec = document.querySelector(".specifications_container");
  const copiedSpec = originalSpec.cloneNode(true);
  specificationsContainer.appendChild(copiedSpec);

  setupSpecificationContainer(copiedSpec);
}

async function handleSpecifications(event) {
  event.preventDefault();
  const specificationContainers =
    document.querySelectorAll(".specifications_container");

  const specifications = [];

  specificationContainers.forEach((container) => {
    const marker = container.querySelector('[name="marker"]').value;
    const markerAmount = container.querySelector('[name="count_per_group"]').value;
    const notCombine = container.querySelector('[name="no_combi_with"]').value;
    const combine = container.querySelector('[name="combi_with"]').value;
    const combineAmount = container.querySelector('[name="combi_with_amount"]').value;
    const cap = container.querySelector('[name="spec_cap"]').checked;
    const capAmount = container.querySelector('[name="cap_amount"]').value;
    
    specifications.push({
      marker: marker,
      markerAmount: markerAmount,
      notCombine: notCombine,
      combine: combine,
      combineAmount: combineAmount,
      cap: cap,
      capAmount: capAmount
    })
  }
  )
  const groupAmount = document.getElementById("group_amount").value;
  const csrftoken = document.querySelector('[name="csrfmiddlewaretoken"]').value

  const response = await fetch("handle_specifications", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken
    },
    body: JSON.stringify({
      specifications,
      groupAmount
    })
    });

    const data = await response.json();
    console.log("Reponse", data.groups);
   
  }

function setupSpecificationContainer(container) {
  const markerSelect = container.querySelector('[name="marker"]');
  const forbiddenSelect = container.querySelector('[name="no_combi_with"]');
  const combineSelect = container.querySelector('[name="combi_with"]');

  markerSelect.addEventListener("change", function() {
    updateSpecificationOptions(container);
  });

  forbiddenSelect.addEventListener("change", function() {
    updateSpecificationOptions(container);
  });

  combineSelect.addEventListener("change", function() {
    updateSpecificationOptions(container);
  });

  updateSpecificationOptions(container);
}

function updateSpecificationOptions(container) {
  const markerSelect = container.querySelector('[name="marker"]');
  const forbiddenSelect = container.querySelector('[name="no_combi_with"]');
  const combineSelect = container.querySelector('[name="combi_with"]');

  const selectedMarker = markerSelect.value;
  const forbiddenMarker = forbiddenSelect.value;
  const combineMarker = combineSelect.value;


  Array.from(forbiddenSelect.options).forEach((option) => {
    const isOwnMarker = option.value === selectedMarker;
    const isCombinedMarker = option.value === combineMarker;

    option.disabled = option.value !== "" &&
    (isOwnMarker || isCombinedMarker)
  });

  Array.from(combineSelect.options).forEach((option) => {
    const isForbiddenMarker = option.value === forbiddenMarker;

    option.disabled = option.value !== "" &&
    isForbiddenMarker;
  });

  if (
    forbiddenSelect.value === selectedMarker ||
    forbiddenSelect.value === combineMarker
  ) {
    forbiddenSelect.value = "";
  }

  if (combineSelect.value === forbiddenMarker) {
    combineSelect.value = "";
  }

}