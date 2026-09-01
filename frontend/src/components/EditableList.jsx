import './EditableList.css'

function EditableList({ items, onItemsChange, renderItem, createItem, getItemKey = (item) => item.id }) {
  const updateItem = (index, updated) => {
    onItemsChange(items.map((item, i) => (i === index ? updated : item)))
  }

  const removeItem = (index) => {
    onItemsChange(items.filter((_, i) => i !== index))
  }

  const addItem = () => {
    onItemsChange([...items, createItem()])
  }

  return (
    <div>
      <ul>
        {items.map((item, index) => (
          <li key={getItemKey(item, index)}>
            {renderItem(item, (updated) => updateItem(index, updated))}
            <button onClick={() => removeItem(index)}>Remove</button>
          </li>
        ))}
      </ul>
      <button onClick={addItem}>Add</button>
    </div>
  )
}   

export default EditableList