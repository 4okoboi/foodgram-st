import { useEffect, useState } from 'react'
import styles from './style.module.css'
import { Nav, AccountMenu, LinkComponent } from '../index.js'
import Container from '../container'
import LogoHeader from '../../images/logo-header.png'

const Header = ({ loggedIn, onSignOut, orders }) => {
  const [onlineUsers, setOnlineUsers] = useState(0)
  const [recipeCount, setRecipeCount] = useState(0)

  useEffect(() => {
    const usersSocket = new WebSocket(`ws://${process.env.API_URL || "http://localhost"}/ws/users`)
    const recipesSocket = new WebSocket(`ws://${process.env.API_URL || "http://localhost"}/ws/recipes`)

    usersSocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'user_count') {
          setOnlineUsers(data.count)
        }
      } catch (error) {
        console.error('Invalid user WS message:', event.data)
      }
    }

    recipesSocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'recipe_count') {
          setRecipeCount(data.count)
        }
      } catch (error) {
        console.error('Invalid recipe WS message:', event.data)
      }
    }

    usersSocket.onerror = (e) => console.error('Users WS error:', e)
    recipesSocket.onerror = (e) => console.error('Recipes WS error:', e)

    return () => {
      usersSocket.close()
      recipesSocket.close()
    }
  }, [])

  return (
    <header className={styles.header}>
      <Container>
        <div className={styles.headerContent}>
          <LinkComponent
            className={styles.headerLink}
            title={<img className={styles.headerLogo} src={LogoHeader} alt='Foodgram' />}
            href='/'
          />
          <div className={styles.wsInfo}>
            <span>👥 Онлайн: {onlineUsers}</span>
            <span>📖 Рецептов: {recipeCount}</span>
          </div>
          <Nav
            loggedIn={loggedIn}
            onSignOut={onSignOut}
            orders={orders}
          />
        </div>
      </Container>
    </header>
  )
}

export default Header
