let session_id = null

if (typeof(Storage) !== "undefined") {
    session_id = localStorage.getItem("session_id")
}

// Set constants
const DEBUG = false
const DOM_EVENTS = {
    UIEvent: [
        "load",
    ],
    Event: [
        "change",
        "input",
        "submit",
    ],
    MouseEvent: [
        "click",
    ]
}

function setBooleanProp($target, name, value) {
    /*  Method that sets boolean properties on an element.
    */

    if (value) {
        $target.setAttribute(name, value)
        $target[name] = true
    } else {
        $target[name] = false
    }
}

function setProp($target, name, value) {
    /*  Method that sets a property on an element.
    */

    // Do nothing for custom props
    if (isCustomProp(name)) {
        return

    // Handle boolean values seperately
    } else if (typeof value === 'boolean') {
        setBooleanProp($target, name, value)

    // Handle the rest
    } else {
        $target.setAttribute(name, value)
    }
}

function setProps($target, props) {
    /*  Method that sets multiple properties on an element.
    */

    // Loop over the properties
    Object.keys(props).forEach(name => {

        // Use the setProp method to set the properties
        setProp($target, name, props[name])
    })
}

function createElement(node) {
    /*  Method that creates an DOM element from a node definition.
    */

    // Handle text nodes (e.g. <p>)
    if (typeof node === 'string') {
        return document.createTextNode(node)
    }

    // Create an element of the requested type
    const $el = document.createElement(node.type)

    // Set the properties
    setProps($el, node.props)

    // Create any children
    node.children
        .map(createElement)
        .forEach($el.appendChild.bind($el))

    // Return the element
    return $el
}

function removeBooleanProp($target, name) {
    /*  Remove boolean properties from an element.
    */

    $target.removeAttribute(name)
    $target[name] = false
}

function isEventProp(name) {
    /*  Method that checks if a property is an event property (on...).
    */
    return /^on/.test(name)
}

function extractEventName(name) {
    /*  Method that extracts the event name from the property (on...).
    */

    return name.slice(2).toLowerCase()
}

function isCustomProp(name) {
    /*  Method that checks if a property is a custom property.
    */

    return isEventProp(name) || name === 'forceUpdate'
}

function removeProp($target, name, value) {
    /*  Remove a property from an element
    */

    // Do nothing for custom properties
    if (isCustomProp(name)) {
        return

    // Handle boolean properties seperately
    } else if (typeof value === 'boolean') {
        removeBooleanProp($target, name)

    // Handle all other properties
    } else {
        $target.removeAttribute(name)
    }
}

function updateProp($target, name, newVal, oldVal) {
    /*  Update the value of a property.
    */

    // Remove the value if no new value is provided
    if (!newVal) {
        removeProp($target, name, oldVal)

    // Set the property to the new value
    } else if (!oldVal || newVal !== oldVal) {
        setProp($target, name, newVal)
    }
}

function updateProps($target, newProps, oldProps = {}) {
    /*  Method that handles all updates to the properties of an element.
    */

    // Make a combination of the new and old properties
    const props = Object.assign({}, newProps, oldProps)

    // Loop over the properties and update all of them
    Object.keys(props).forEach(name => {
        updateProp($target, name, newProps[name], oldProps[name])
    })
}

function changed(node1, node2) {
    /*  Method to check if something has changed between an old and new node.
    */

    return typeof node1 !== typeof node2 ||
           typeof node1 === 'string' && node1 !== node2 ||
           node1.type !== node2.type ||
           node1.props && node1.props.forceUpdate
}

function isNil(value) {
    /*  Method that checks if a value is null
    */
    return value == null
}

function updateElement($parent, newNode, oldNode, childNode = $parent.childNodes[0]) {
    /* Update an element.
    */

    // If the old node had no content, add it
    if (isNil(oldNode)) {
        if (DEBUG) console.log("No old node, create a new node:\n", newNode)
        $parent.appendChild(createElement(newNode))

    // If the new node has no content, remove the old
    } else if (isNil(newNode)) {
        if (DEBUG) console.log("No new node, removing node:\n", childNode)
        $parent.removeChild(childNode)
        return -1

    // If the node has changed, replace it
    } else if (changed(newNode, oldNode)) {
        if (DEBUG) console.log("Node changed.\n\nOld node:\n", oldNode, "\nNew node:\n", newNode)
        $parent.replaceChild(createElement(newNode), childNode)

    // If the new node contains other nodes, process them
    } else if (newNode.type) {

        // Update the properties of the node
        updateProps(childNode, newNode.props, oldNode.props)

        // Keep track of any adjustments (for removing elements)
        let adjustment = 0;
        for (let i = 0; i < Math.max(newNode.children.length, oldNode.children.length); i++) {

            // Update each child element
            adjustment += updateElement(
                childNode,
                newNode.children[i],
                oldNode.children[i],
                childNode.childNodes[i + adjustment]
            )
        }
    }
    return 0
}

function clearInputField(identifier) {
    /*  Method that clears the value of an input field.
    */

    if (identifier != "") {
        $("[identifier='" + identifier + "']")[0].value = ""
        $("[identifier='" + identifier + "']")[0].focus()
    }
}

function getIdentifier(event) {
    /*  Get the identifier from the event target.
    */

    let target = event.target || {}
    let attributes = target.attributes || {}
    let identifier = attributes.identifier || {}
    identifier = identifier.value

    if (identifier == undefined){
        identifier = target.id || ""
    }
    return identifier
}

function getElementByIdentifier(identifier) {
    return $("[identifier='" + identifier + "']")[0]
}

// Get a reference to the root element
let $root = document.getElementById('root')

// Initialize other parameters
let old_dom = undefined

// Create a socket connection
let socket = io.connect('http://' + document.domain + ':' + location.port)

// Handle connection events
socket.on('connect', function() {

    // Hide the overlay
    document.getElementById("overlay").style.display = "none"

    if (session_id) {
        socket.emit("RESTORE_SESSION", {"session_id": session_id})
    } else {
        socket.emit("REQUEST_SESSION", {})
    }
})

socket.on('disconnect', function () {
    document.getElementById("overlay").style.display = "block"
})

socket.on('reconnect', function() {
    socket.emit('DOM_EVENT', {'DOMEventCategory': 'UIEvent load', 'link_target': location.pathname, "link_search": location.search, "link_anchor": location.hash})
})

socket.on('STORE_SESSION', function(event) {
    session_id = event["session_id"]
    localStorage.setItem("session_id", session_id)
    console.log("Store the session id in local storage")
})

// Handle the incoming VDOM when an update is received
socket.on('VDOM_UPDATE', function(new_dom) {

    if (DEBUG) console.group("Handle VDOM update")

    // Update
    if (typeof(old_dom) != undefined){
        updateElement($root, new_dom, old_dom)
        old_dom = new_dom
    } 

    // Create new
    else {
        updateElement($root, old_dom)
    }

    if (DEBUG) console.groupEnd()

})

// Reflect the change in location by pushing details to the history
socket.on('NAVIGATION_EVENT', function(details) {
    window.history.pushState({"details": details}, "", details["link_target"])
})

// Handle events to clear input fields
socket.on('CLEAR_INPUT_FIELD', function(details) {
    clearInputField(details["identifier"])
})


// Loop over the enabled DOM events
for (DOMEvent in DOM_EVENTS){

    // Get the types for this group of events
    let DOMEventTypes = DOM_EVENTS[DOMEvent]

    DOMEventTypes.map(function(DOMEventType){

        // Create a unique name by combining the group and the type of event
        let DOMEventCategory = DOMEvent + ' ' + DOMEventType

        // Add an event listener that captures all of these events
        document.addEventListener(DOMEventType, function(event){

            // Prevent any event from doing something
            event.preventDefault()

            // Get the identifier of the target (if any)
            let identifier = getIdentifier(event)

            // Get the value of the target (if any)
            let value = event.target.value || undefined

            // Construct the message to send to the backend
            let message = {'DOMEventCategory': DOMEventCategory}

            // Handle specific cases first
            if (DOMEventCategory == "UIEvent load"){
                message = Object.assign({}, message, {'link_target': location.pathname, "link_search": location.search, "link_anchor": location.hash})
            } else {
                console.log(event)
                message = Object.assign({}, message, {
                    'target': identifier || '',
                    'value': value || ''
                })
            }

            // Send the message to the backend
            socket.emit('DOM_EVENT', message)

        }, true)
    })

}

window.addEventListener("popstate", function(event) {
    console.log(location)
    socket.emit('DOM_EVENT', {"DOMEventCategory": "UIEvent load", "link_target": location.pathname, "link_search": location.search, "link_anchor": location.hash})
})
