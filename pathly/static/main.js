addEventListener("DOMContentLoaded", (event) => {
  
  // creating variables for the elements
  const uploadForm = document.getElementById("kml-upload-form");
  const addSpecButton = document.getElementById("add-spec-button");
  const specForm = document.getElementById("spec_form");
  const addGroupButton = document.querySelector("#add_group");
  const addToGroupButton = document.querySelector("#add_to_group");
  const removeFromGroupButton = document.querySelector("#remove_from_group");
  const submitManualForm = document.querySelector("#manual_sorting_button");
  const routesForm = document.querySelector("#routes_form");

  let activeGroup = null;
  let groupCount = 0;

  // submitting forms
  if (uploadForm) {
  uploadForm.addEventListener("submit", uploadKml)
  }

  if (addSpecButton) {
  addSpecButton.addEventListener("click", addSpecification)
  }

  // specification event handler
  if (specForm) {
    document.getElementById("spec_form").addEventListener("submit", handleSpecifications)
    
    const specificationContainers = document.querySelectorAll(".specifications_container");
    specificationContainers.forEach(function(container) {
      setupSpecificationContainer(container);
    });
  } 
  
  // gorup button event handlers
  if (addGroupButton) {
    addGroupButton.addEventListener("click", () => {
      groupCount++;

      const createdGroups = document.getElementById("created_groups");
      const newGroup = document.createElement("div");
      const groupTitle = document.createElement("h3");
      const groupList = document.createElement("ul");
      
      newGroup.classList.add("manual_group");
      groupList.classList.add("group_location_list");
      groupList.setAttribute("id", `group_${groupCount}`);
      groupTitle.textContent = `Group ${groupCount}`;

      newGroup.append(groupTitle, groupList);
      createdGroups.appendChild(newGroup);

      // make activeGroup the currently created group so newly added locations go there
      activeGroup = groupList;
    });
  }

  if (addToGroupButton) {
    addToGroupButton.addEventListener("click", () => {
      if (!activeGroup) {
        alert("Please create a group first.");
        return;
      }

      const selectedLocations = document.querySelectorAll(".location_check:checked");

      selectedLocations.forEach((checkbox) => {
        const locationItem = checkbox.closest(".location_item");
        const allOriginalLists = Array.from(document.querySelectorAll(".location_list"));
        const originalContainer = locationItem.closest(".location_list");

        // store original list where the location belongs, so remove button works
        locationItem.dataset.originalListIndex =
        allOriginalLists.indexOf(originalContainer);

        checkbox.checked = false;
        activeGroup.appendChild(locationItem);
      })
    })
    }
  
  if (removeFromGroupButton) {
    removeFromGroupButton.addEventListener("click", () => {
      const selectedLocations = document.querySelectorAll(".group_location_list .location_check:checked");

      const allOriginalLists = document.querySelectorAll(".location_list");

      selectedLocations.forEach((checkbox) => {
        const locationItem = checkbox.closest(".location_item");

        // find original list where location belongs
        const originalListIndex = Number(
          locationItem.dataset.originalListIndex
        );

        const originalContainer = allOriginalLists[originalListIndex];

        if (!originalContainer) {
          return;
        }

        checkbox.checked = false;
        originalContainer.appendChild(locationItem);
      })
    })
  }
  if (submitManualForm) {
    submitManualForm.addEventListener("click", sortManualGroups);
  }

  if (routesForm) {
    routesForm.addEventListener("submit", handleRoutesForm);
  }

});



// function to handle uploaded KML file
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

// function to add specification
function addSpecification(event) {
  event.preventDefault();
  const specificationsContainer = document.getElementById("spec_parent_container");
  const originalSpec = document.querySelector(".specifications_container");
  const copiedSpec = originalSpec.cloneNode(true);
  specificationsContainer.appendChild(copiedSpec);

  setupSpecificationContainer(copiedSpec);
}

// function to handle specification on the backend
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

async function sortManualGroups(event) {
  event.preventDefault();

  const csrftoken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
  
  const groups = Array.from(
    document.querySelectorAll(".manual_group")).map((group) => {
      const groupList = group.querySelector(".group_location_list");
      
      const locationIds = Array.from(
        groupList.querySelectorAll(".location_check")).map((checkbox) => checkbox.value);

      return {
        groupId: groupList.id,
        locationIds: locationIds,
      };    
    });
  
  const response = await fetch("sort_manually", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({
      groups: groups,
    }),
  });

  const data = await response.json();
  if (data === "success") {
    console.log("success")
    document.querySelector("#manual_sorting_form").style.display = "none";
    document.getElementById("finished_grouping").style.display = "block";
    alert("Groups sorted successfully! Head on to routes.");
  }
}

function handleRoutesForm {
  // TODO
}

