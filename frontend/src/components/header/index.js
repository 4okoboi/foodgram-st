import { useEffect, useState } from 'react'
import styles from './style.module.css'
import { Nav, AccountMenu, LinkComponent } from '../index.js'
import Container from '../container'
import LogoHeader from '../../images/logo-header.png'

const Header = ({ loggedIn, onSignOut, orders }) => {
  const [onlineUsers, setOnlineUsers] = useState(0)
  const [recipeCount, setRecipeCount] = useState(0)

  useEffect(() => {
    const usersSocket = new WebSocket(`ws://89.208.113.95/ws/users/`)

    usersSocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'update_user_count') {
          setOnlineUsers(data.total)
        }
      } catch (error) {
        console.error('Invalid user WS message:', event.data)
      }
    }

    usersSocket.onerror = (e) => console.error('Users WS error:', e)

    return () => {
      usersSocket.close()
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
