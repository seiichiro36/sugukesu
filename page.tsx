'use client'

import { useState, FormEvent } from 'react'

// 型定義
interface Book {
  title: string
  author: string
  publication_year: number
  isbn: string
  price: number
  description: string
}

export default function BookCreatePage() {
  // フォーム状態の初期値
  const [bookData, setBookData] = useState<Book>({
    title: '',
    author: '',
    publication_year: 2023,
    isbn: '',
    price: 0,
    description: ''
  })

  // 送信ハンドラー
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    
    try {
      const response = await fetch('http://127.0.0.1:8000/books/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bookData)
      })

      if (response.status === 200) {
        alert('書籍が正常に登録されました')
        // フォームをリセット
        setBookData({
          title: '',
          author: '',
          publication_year: 2023,
          isbn: '',
          price: 0,
          description: ''
        })
      }
    } catch (error) {
      console.error('エラーが発生しました:', error)
      alert('書籍の登録に失敗しました')
    }
  }

  // 入力変更ハンドラー
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    
    // 数値型の項目は数値に変換
    const formattedValue = 
      name === 'publication_year' || name === 'price' 
        ? Number(value) 
        : value

    setBookData(prev => ({
      ...prev,
      [name]: formattedValue
    }))
  }

  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded-lg shadow-md">
      <h1 className="text-2xl font-bold mb-6">新規書籍登録</h1>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-2">タイトル</label>
          <input
            type="text"
            name="title"
            value={bookData.title}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>

        <div>
          <label className="block mb-2">著者</label>
          <input
            type="text"
            name="author"
            value={bookData.author}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>

        <div>
          <label className="block mb-2">出版年</label>
          <input
            type="number"
            name="publication_year"
            value={bookData.publication_year}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>

        <div>
          <label className="block mb-2">ISBN</label>
          <input
            type="text"
            name="isbn"
            value={bookData.isbn}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>

        <div>
          <label className="block mb-2">価格</label>
          <input
            type="number"
            name="price"
            value={bookData.price}
            onChange={handleChange}
            required
            step="0.01"
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>

        <div>
          <label className="block mb-2">説明</label>
          <textarea
            name="description"
            value={bookData.description}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-md"
            rows={4}
          />
        </div>

        <button 
          type="submit" 
          className="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 transition"
        >
          書籍を登録
        </button>
      </form>
    </div>
  )
}