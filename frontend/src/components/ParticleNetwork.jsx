import { useRef, useEffect } from 'react'

const DARK_COLORS = [
  '#4F7CFF', '#00D1FF', '#9B6DFF', '#FF5FD2',
  '#6B8FFF', '#33DBFF', '#B08AFF', '#FF7FDE',
  '#4F7CFF', '#00D1FF',
]

const LIGHT_COLORS = [
  '#4338ca', '#2563eb', '#7c3aed', '#0e7490',
  '#4f46e5', '#6d28d9', '#0369a1', '#4c1d95',
  '#3730a3', '#155e75',
]

const DARK_ORBS = [
  { color: '79, 124, 255', size: 350 },
  { color: '0, 209, 255', size: 300 },
  { color: '155, 109, 255', size: 280 },
  { color: '255, 95, 210', size: 240 },
  { color: '79, 124, 255', size: 200 },
]

const LIGHT_ORBS = [
  { color: '99, 102, 241', size: 250 },
  { color: '59, 130, 246', size: 220 },
  { color: '6, 182, 212', size: 200 },
  { color: '139, 92, 246', size: 180 },
]

const ParticleNetwork = ({ className = '', theme = 'dark' }) => {
  const canvasRef = useRef(null)
  const animationRef = useRef(null)
  const particlesRef = useRef([])
  const orbsRef = useRef([])
  const trailRef = useRef([])
  const ripplesRef = useRef([])
  const tempNodesRef = useRef([])
  const mouseRef = useRef({ x: -1000, y: -1000 })
  const smoothMouseRef = useRef({ x: -1000, y: -1000 })
  const dimensionsRef = useRef({ width: 0, height: 0 })
  const parallaxRef = useRef({ x: 0, y: 0 })

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const isDark = theme === 'dark'
    const PARTICLE_COLORS = isDark ? DARK_COLORS : LIGHT_COLORS
    const ORB_COLORS = isDark ? DARK_ORBS : LIGHT_ORBS

    const ctx = canvas.getContext('2d')
    let particles = particlesRef.current
    let orbs = orbsRef.current
    let trail = trailRef.current
    let ripples = ripplesRef.current
    let tempNodes = tempNodesRef.current

    const resize = () => {
      const rect = canvas.parentElement.getBoundingClientRect()
      const dpr = window.devicePixelRatio || 1
      canvas.width = rect.width * dpr
      canvas.height = rect.height * dpr
      canvas.style.width = `${rect.width}px`
      canvas.style.height = `${rect.height}px`
      ctx.scale(dpr, dpr)
      dimensionsRef.current = { width: rect.width, height: rect.height }

      initParticles(rect.width, rect.height)
      initOrbs(rect.width, rect.height)
    }

    const initOrbs = (w, h) => {
      orbs = ORB_COLORS.map((o, i) => ({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.1,
        vy: (Math.random() - 0.5) * 0.08,
        size: o.size + Math.random() * 100,
        color: o.color,
        phase: i * 1.2,
      }))
      orbsRef.current = orbs
    }

    const initParticles = (w, h) => {
      const count = isDark
        ? Math.min(400, Math.floor((w * h) / 2600))
        : Math.min(320, Math.floor((w * h) / 3200))
      particles = []

      for (let i = 0; i < count; i++) {
        const isHub = Math.random() < (isDark ? 0.1 : 0.09)

        const x = Math.random() * w
        const y = Math.random() * h

        const distFromCenter = 0

        const depthLayer = isDark
          ? (Math.random() < 0.1 ? 'far' : Math.random() < 0.3 ? 'mid' : 'near')
          : 'near'

        const layerScale = depthLayer === 'far' ? 0.5 : depthLayer === 'mid' ? 0.8 : 1.0
        const layerOpacity = depthLayer === 'far' ? 0.4 : depthLayer === 'mid' ? 0.7 : 1.0
        const layerSpeed = depthLayer === 'far' ? 0.24 : depthLayer === 'mid' ? 0.42 : 0.6

        particles.push({
          x,
          y,
          baseX: x,
          baseY: y,
          vx: (Math.random() - 0.5) * layerSpeed,
          vy: (Math.random() - 0.5) * layerSpeed,
          radius: isHub
            ? (isDark ? Math.random() * 3 + 2.5 : Math.random() * 3.5 + 3) * layerScale
            : (isDark ? Math.random() * 1.5 + 0.5 : Math.random() * 1.8 + 0.6) * layerScale,
          color: PARTICLE_COLORS[Math.floor(Math.random() * PARTICLE_COLORS.length)],
          opacity: isHub
            ? (isDark ? 0.95 * layerOpacity : 0.95)
            : (isDark ? (Math.random() * 0.4 + 0.2) * layerOpacity : Math.random() * 0.5 + 0.35),
          pulseSpeed: isHub ? Math.random() * 0.04 + 0.015 : Math.random() * 0.025 + 0.008,
          pulsePhase: Math.random() * Math.PI * 2,
          isHub,
          activeScale: 1,
          activeOpacity: 0,
          rippleBoost: 0,
          depthLayer,
          layerScale,
          layerOpacity,
          sinPhaseX: Math.random() * Math.PI * 2,
          sinPhaseY: Math.random() * Math.PI * 2,
          sinSpeedX: (Math.random() * 0.36 + 0.12) * layerSpeed,
          sinSpeedY: (Math.random() * 0.3 + 0.1) * layerSpeed,
          sinAmpX: (Math.random() * 15 + 5) * layerScale,
          sinAmpY: (Math.random() * 12 + 4) * layerScale,
          distFromCenter,
        })
      }
      for (const p of particles) {
        p.baseX = p.x
        p.baseY = p.y
      }
      particlesRef.current = particles
    }

    const spawnRipple = (x, y) => {
      if (ripples.length >= 3) return
      ripples.push({ x, y, radius: 0, maxRadius: 180, life: 1, speed: 3 })
      tempNodes.push({
        x, y, radius: 3.5, life: 1,
        color: PARTICLE_COLORS[Math.floor(Math.random() * PARTICLE_COLORS.length)],
      })
      ripplesRef.current = ripples
      tempNodesRef.current = tempNodes
    }

    const updateRipples = () => {
      for (let i = ripples.length - 1; i >= 0; i--) {
        const r = ripples[i]
        r.radius += r.speed
        r.life = 1 - (r.radius / r.maxRadius) ** 0.7
        if (r.life <= 0) { ripples.splice(i, 1); continue }

        for (const p of particles) {
          const dx = p.x - r.x
          const dy = p.y - r.y
          const dist = Math.sqrt(dx * dx + dy * dy)
          const waveFront = Math.abs(dist - r.radius)
          if (waveFront < 20) {
            const intensity = (1 - waveFront / 20) * r.life * r.life
            const pushForce = intensity * 0.1
            if (dist > 0) {
              p.vx += (dx / dist) * pushForce
              p.vy += (dy / dist) * pushForce
            }
            p.rippleBoost = Math.max(p.rippleBoost, intensity * 0.7)
          }
        }
      }

      for (let i = tempNodes.length - 1; i >= 0; i--) {
        tempNodes[i].life -= 0.015
        if (tempNodes[i].life <= 0) tempNodes.splice(i, 1)
      }
    }

    const drawRipples = () => {
      const ringColor = isDark ? '0, 209, 255' : '99, 102, 241'
      for (const r of ripples) {
        const fadeAlpha = r.life * r.life
        ctx.beginPath()
        ctx.arc(r.x, r.y, r.radius, 0, Math.PI * 2)
        ctx.strokeStyle = `rgba(${ringColor}, ${fadeAlpha * (isDark ? 0.15 : 0.15)})`
        ctx.lineWidth = (isDark ? 0.8 : 1) * fadeAlpha
        ctx.stroke()

        if (r.radius > 5) {
          ctx.beginPath()
          ctx.arc(r.x, r.y, r.radius, 0, Math.PI * 2)
          const rippleGlow = ctx.createRadialGradient(
            r.x, r.y, Math.max(0, r.radius - 10),
            r.x, r.y, r.radius + 10
          )
          rippleGlow.addColorStop(0, 'transparent')
          rippleGlow.addColorStop(0.5, `rgba(${ringColor}, ${fadeAlpha * (isDark ? 0.03 : 0.03)})`)
          rippleGlow.addColorStop(1, 'transparent')
          ctx.fillStyle = rippleGlow
          ctx.fill()
        }
      }
    }

    const drawTempNodes = () => {
      for (const node of tempNodes) {
        const ease = node.life * node.life * node.life
        const r = node.radius * (0.8 + (1 - ease) * 0.6)

        const glowR = r * 5
        ctx.beginPath()
        ctx.arc(node.x, node.y, glowR, 0, Math.PI * 2)
        const glow = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, glowR)
        glow.addColorStop(0, node.color)
        glow.addColorStop(0.5, node.color)
        glow.addColorStop(1, 'transparent')
        ctx.fillStyle = glow
        ctx.globalAlpha = ease * 0.08
        ctx.fill()

        ctx.beginPath()
        ctx.arc(node.x, node.y, r, 0, Math.PI * 2)
        ctx.fillStyle = node.color
        ctx.globalAlpha = ease * 0.7
        ctx.fill()

        ctx.beginPath()
        ctx.arc(node.x, node.y, r * 0.35, 0, Math.PI * 2)
        ctx.fillStyle = '#ffffff'
        ctx.globalAlpha = ease * 0.5
        ctx.fill()

        const connRadius = 100 * ease
        for (const p of particles) {
          const dx = p.x - node.x
          const dy = p.y - node.y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < connRadius) {
            const strength = (1 - dist / connRadius) * ease
            ctx.beginPath()
            ctx.moveTo(node.x, node.y)
            ctx.lineTo(p.x, p.y)
            const grad = ctx.createLinearGradient(node.x, node.y, p.x, p.y)
            grad.addColorStop(0, node.color)
            grad.addColorStop(1, p.color)
            ctx.strokeStyle = grad
            ctx.globalAlpha = strength * 0.2
            ctx.lineWidth = strength * 0.8
            ctx.stroke()
          }
        }
        ctx.globalAlpha = 1
      }
    }

    const drawOrbs = (time) => {
      for (const orb of orbs) {
        orb.x += orb.vx
        orb.y += orb.vy
        const { width, height } = dimensionsRef.current
        if (orb.x < -orb.size) orb.x = width + orb.size
        if (orb.x > width + orb.size) orb.x = -orb.size
        if (orb.y < -orb.size) orb.y = height + orb.size
        if (orb.y > height + orb.size) orb.y = -orb.size

        const breathe = Math.sin(time * 0.003 + orb.phase) * 0.2 + 0.8
        const size = orb.size * breathe

        ctx.beginPath()
        ctx.arc(orb.x, orb.y, size, 0, Math.PI * 2)
        const grad = ctx.createRadialGradient(orb.x, orb.y, 0, orb.x, orb.y, size)
        const orbAlpha = isDark ? 0.08 : 0.04
        const orbMid = isDark ? 0.035 : 0.015
        grad.addColorStop(0, `rgba(${orb.color}, ${orbAlpha})`)
        grad.addColorStop(0.4, `rgba(${orb.color}, ${orbMid})`)
        grad.addColorStop(1, 'transparent')
        ctx.fillStyle = grad
        ctx.fill()
      }
    }

    const drawTrail = () => {
      for (let i = trail.length - 1; i >= 0; i--) {
        const t = trail[i]
        t.life -= 0.02
        t.x += t.vx
        t.y += t.vy
        t.vx *= 0.96
        t.vy *= 0.96
        if (t.life <= 0) { trail.splice(i, 1); continue }

        ctx.beginPath()
        ctx.arc(t.x, t.y, t.radius * t.life, 0, Math.PI * 2)
        ctx.fillStyle = t.color
        ctx.globalAlpha = t.life * (isDark ? 0.3 : 0.25)
        ctx.fill()
      }
      ctx.globalAlpha = 1
    }

    const spawnTrailParticles = () => {
      const mouse = smoothMouseRef.current
      if (mouse.x < -500) return
      if (trail.length > 30) return

      for (let i = 0; i < 1; i++) {
        trail.push({
          x: mouse.x + (Math.random() - 0.5) * 6,
          y: mouse.y + (Math.random() - 0.5) * 6,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          radius: Math.random() * 1.5 + 0.5,
          color: PARTICLE_COLORS[Math.floor(Math.random() * PARTICLE_COLORS.length)],
          life: 1,
        })
      }
      trailRef.current = trail
    }

    const drawParticle = (p, time) => {
      const twinkle = Math.sin(time * p.pulseSpeed * 3 + p.pulsePhase) > 0.85 ? 1.4 : 1.0
      const pulse = (Math.sin(time * p.pulseSpeed + p.pulsePhase) * 0.4 + 0.6) * twinkle
      const baseAlpha = p.opacity * pulse
      const rippleAlpha = p.rippleBoost * (isDark ? 0.5 : 0.3)
      const alpha = Math.min(1, baseAlpha + p.activeOpacity * (isDark ? 0.5 : 0.4) + rippleAlpha)
      const scale = p.activeScale + p.rippleBoost * (isDark ? 0.3 : 0.2)
      const r = p.radius * scale

      if (isDark) {
        if (p.isHub) {
          const bloomRadius = r * 10
          ctx.beginPath()
          ctx.arc(p.x, p.y, bloomRadius, 0, Math.PI * 2)
          const bloomGrad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, bloomRadius)
          bloomGrad.addColorStop(0, p.color)
          bloomGrad.addColorStop(0.2, p.color)
          bloomGrad.addColorStop(1, 'transparent')
          ctx.fillStyle = bloomGrad
          ctx.globalAlpha = 0.1 + p.activeOpacity * 0.12 + p.rippleBoost * 0.15
          ctx.fill()
        }

        if (p.isHub || scale > 1.05 || p.radius > 0.8) {
          const glowRadius = r * (p.isHub ? 7 : 4)
          ctx.beginPath()
          ctx.arc(p.x, p.y, glowRadius, 0, Math.PI * 2)
          const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, glowRadius)
          gradient.addColorStop(0, p.color)
          gradient.addColorStop(0.35, p.color)
          gradient.addColorStop(1, 'transparent')
          ctx.fillStyle = gradient
          ctx.globalAlpha = alpha * (p.isHub ? 0.4 : 0.18) * (1 + p.activeOpacity * 1.2 + p.rippleBoost * 0.8)
          ctx.fill()
        }
      } else {
        if (p.isHub) {
          const bloomRadius = r * 8 * (0.8 + p.activeOpacity * 0.8)
          ctx.beginPath()
          ctx.arc(p.x, p.y, bloomRadius, 0, Math.PI * 2)
          const bloomGrad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, bloomRadius)
          bloomGrad.addColorStop(0, p.color)
          bloomGrad.addColorStop(0.25, p.color)
          bloomGrad.addColorStop(1, 'transparent')
          ctx.fillStyle = bloomGrad
          ctx.globalAlpha = 0.12 + p.activeOpacity * 0.15
          ctx.fill()
        }

        if (p.isHub || scale > 1.1 || p.radius > 1.2) {
          const glowRadius = r * (p.isHub ? 5 : 3.2)
          ctx.beginPath()
          ctx.arc(p.x, p.y, glowRadius, 0, Math.PI * 2)
          const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, glowRadius)
          gradient.addColorStop(0, p.color)
          gradient.addColorStop(0.4, p.color)
          gradient.addColorStop(1, 'transparent')
          ctx.fillStyle = gradient
          ctx.globalAlpha = alpha * (p.isHub ? 0.35 : 0.15) * (1 + p.activeOpacity * 1.2)
          ctx.fill()
        }
      }

      ctx.beginPath()
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2)
      ctx.fillStyle = p.color
      ctx.globalAlpha = alpha
      ctx.fill()

      if (p.isHub && isDark) {
        ctx.beginPath()
        ctx.arc(p.x, p.y, r * 0.45, 0, Math.PI * 2)
        ctx.fillStyle = '#ffffff'
        ctx.globalAlpha = alpha * 0.7
        ctx.fill()
      }

      p.rippleBoost *= 0.92
      ctx.globalAlpha = 1
    }

    const drawConnections = (particles) => {
      const connectionDistance = isDark ? 130 : 120
      const hubConnectionDistance = isDark ? 200 : 210
      const mouse = smoothMouseRef.current
      const mouseActive = mouse.x > -500
      const hasActiveRipple = ripples.length > 0

      for (let i = 0; i < particles.length; i++) {
        const pi = particles[i]
        if (isDark && pi.depthLayer === 'far') continue

        for (let j = i + 1; j < particles.length; j++) {
          const pj = particles[j]
          if (isDark && pj.depthLayer === 'far') continue

          const dx = pi.x - pj.x
          const dy = pi.y - pj.y
          const distSq = dx * dx + dy * dy
          const threshold = pi.isHub || pj.isHub ? hubConnectionDistance : connectionDistance

          if (distSq > threshold * threshold) continue

          const dist = Math.sqrt(distSq)
          let opacity = isDark
            ? (1 - dist / threshold) * (pi.isHub || pj.isHub ? 0.3 : 0.15)
            : (1 - dist / threshold) * (pi.isHub || pj.isHub ? 0.25 : 0.14)

          if (mouseActive) {
            const midX = (pi.x + pj.x) / 2
            const midY = (pi.y + pj.y) / 2
            const mouseDist = Math.sqrt((mouse.x - midX) ** 2 + (mouse.y - midY) ** 2)
            if (mouseDist < 280) {
              const boost = ((1 - mouseDist / 280) ** 1.5) * (isDark ? 0.5 : 0.6)
              opacity = Math.min(isDark ? 0.7 : 0.85, opacity + boost)
            }
          }

          if (hasActiveRipple) {
            const midX = (pi.x + pj.x) / 2
            const midY = (pi.y + pj.y) / 2
            for (const r of ripples) {
              const rDist = Math.sqrt((r.x - midX) ** 2 + (r.y - midY) ** 2)
              const waveDist = Math.abs(rDist - r.radius)
              if (waveDist < 40) {
                const intensity = (1 - waveDist / 40) * r.life
                opacity = Math.min(isDark ? 0.8 : 0.9, opacity + intensity * (isDark ? 0.5 : 0.5))
              }
            }
          }

          const rippleLineBoost = Math.max(pi.rippleBoost, pj.rippleBoost)
          opacity = Math.min(isDark ? 0.8 : 0.9, opacity + rippleLineBoost * 0.3)

          ctx.beginPath()
          ctx.moveTo(pi.x, pi.y)
          ctx.lineTo(pj.x, pj.y)

          if (pi.isHub || pj.isHub) {
            const grad = ctx.createLinearGradient(pi.x, pi.y, pj.x, pj.y)
            grad.addColorStop(0, pi.color)
            grad.addColorStop(1, pj.color)
            ctx.strokeStyle = grad
            ctx.globalAlpha = opacity
            ctx.lineWidth = isDark ? 0.8 : 0.9
          } else {
            ctx.strokeStyle = isDark ? 'rgba(79, 124, 255, 1)' : 'rgba(67, 56, 202, 1)'
            ctx.globalAlpha = opacity
            ctx.lineWidth = isDark ? 0.4 : 0.55
          }
          ctx.stroke()
          ctx.globalAlpha = 1
        }
      }
    }

    const drawMouseWeb = (particles) => {
      const mouse = smoothMouseRef.current
      if (mouse.x < -500) return

      const radius = isDark ? 280 : 280
      const cursorColor = isDark ? '0, 209, 255' : '67, 56, 202'

      ctx.beginPath()
      ctx.arc(mouse.x, mouse.y, isDark ? 4 : 4, 0, Math.PI * 2)
      ctx.fillStyle = `rgb(${cursorColor})`
      ctx.globalAlpha = 0.9
      ctx.fill()

      ctx.beginPath()
      ctx.arc(mouse.x, mouse.y, isDark ? 35 : 35, 0, Math.PI * 2)
      const cursorGlow = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, isDark ? 35 : 35)
      cursorGlow.addColorStop(0, `rgba(${cursorColor}, ${isDark ? 0.4 : 0.3})`)
      cursorGlow.addColorStop(0.5, `rgba(${cursorColor}, ${isDark ? 0.12 : 0.08})`)
      cursorGlow.addColorStop(1, 'transparent')
      ctx.fillStyle = cursorGlow
      ctx.globalAlpha = 1
      ctx.fill()

      ctx.beginPath()
      ctx.arc(mouse.x, mouse.y, isDark ? 100 : 80, 0, Math.PI * 2)
      const outerGlow = ctx.createRadialGradient(mouse.x, mouse.y, 20, mouse.x, mouse.y, isDark ? 100 : 80)
      outerGlow.addColorStop(0, `rgba(${cursorColor}, ${isDark ? 0.07 : 0.05})`)
      outerGlow.addColorStop(1, 'transparent')
      ctx.fillStyle = outerGlow
      ctx.fill()

      for (const p of particles) {
        if (isDark && p.depthLayer === 'far') continue
        const dx = mouse.x - p.x
        const dy = mouse.y - p.y
        const dist = Math.sqrt(dx * dx + dy * dy)

        if (dist < radius) {
          const strength = 1 - dist / radius
          const opacity = strength * strength * (isDark ? 0.5 : 0.55)

          ctx.beginPath()
          ctx.moveTo(mouse.x, mouse.y)
          ctx.lineTo(p.x, p.y)
          const grad = ctx.createLinearGradient(mouse.x, mouse.y, p.x, p.y)
          grad.addColorStop(0, `rgba(${cursorColor}, 0.8)`)
          grad.addColorStop(0.6, p.color)
          grad.addColorStop(1, p.color)
          ctx.strokeStyle = grad
          ctx.globalAlpha = opacity
          ctx.lineWidth = strength * (isDark ? 1.5 : 1.5) + 0.2
          ctx.stroke()
        }
      }
      ctx.globalAlpha = 1
    }

    const drawVignette = () => {
      if (!isDark) return
      const { width, height } = dimensionsRef.current

      const vignette = ctx.createRadialGradient(
        width * 0.5, height * 0.5, width * 0.25,
        width * 0.5, height * 0.5, width * 0.7
      )
      vignette.addColorStop(0, 'transparent')
      vignette.addColorStop(0.6, 'transparent')
      vignette.addColorStop(0.85, 'rgba(5, 8, 22, 0.35)')
      vignette.addColorStop(1, 'rgba(5, 8, 22, 0.65)')
      ctx.fillStyle = vignette
      ctx.fillRect(0, 0, width, height)
    }

    const updateParticles = (time) => {
      const { width, height } = dimensionsRef.current
      const mouse = smoothMouseRef.current

      const raw = mouseRef.current
      smoothMouseRef.current = {
        x: smoothMouseRef.current.x + (raw.x - smoothMouseRef.current.x) * 0.12,
        y: smoothMouseRef.current.y + (raw.y - smoothMouseRef.current.y) * 0.12,
      }

      if (raw.x > -500) {
        parallaxRef.current = {
          x: (raw.x / width - 0.5) * (isDark ? 12 : 18),
          y: (raw.y / height - 0.5) * (isDark ? 12 : 18),
        }
      }

      const px = parallaxRef.current.x
      const py = parallaxRef.current.y

      for (const p of particles) {
        if (isDark) {
          const sinX = Math.sin(time * 0.001 * p.sinSpeedX + p.sinPhaseX) * p.sinAmpX
          const sinY = Math.cos(time * 0.00075 * p.sinSpeedY + p.sinPhaseY) * p.sinAmpY
          p.x = p.baseX + sinX + p.vx * 0.5
          p.y = p.baseY + sinY + p.vy * 0.5
        } else {
          p.x += p.vx + px * 0.03
          p.y += p.vy + py * 0.03
        }

        if (isDark) {
          p.baseX += px * 0.01
          p.baseY += py * 0.01
        }

        if (p.x < -20) { p.x = width + 20; p.baseX = width + 20 }
        if (p.x > width + 20) { p.x = -20; p.baseX = -20 }
        if (p.y < -20) { p.y = height + 20; p.baseY = height + 20 }
        if (p.y > height + 20) { p.y = -20; p.baseY = -20 }

        const dx = mouse.x - p.x
        const dy = mouse.y - p.y
        const dist = Math.sqrt(dx * dx + dy * dy)

        const attractRadius = isDark ? 250 : 300
        if (dist < attractRadius && dist > 0) {
          const force = ((attractRadius - dist) / attractRadius) ** 1.5 * (isDark ? 0.04 : 0.07)
          p.vx += (dx / dist) * force
          p.vy += (dy / dist) * force
          const proximity = 1 - dist / attractRadius
          p.activeScale += (1 + proximity * (isDark ? 1.0 : 1.5) - p.activeScale) * 0.12
          p.activeOpacity += (proximity - p.activeOpacity) * 0.12
        } else {
          p.activeScale += (1 - p.activeScale) * 0.03
          p.activeOpacity += (0 - p.activeOpacity) * 0.03
        }

        const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy)
        const maxSpeed = isDark ? (p.isHub ? 0.4 : 0.6) : (p.isHub ? 0.7 : 1.0)
        if (speed > maxSpeed) {
          p.vx = (p.vx / speed) * maxSpeed
          p.vy = (p.vy / speed) * maxSpeed
        }

        p.vx *= isDark ? 0.97 : 0.985
        p.vy *= isDark ? 0.97 : 0.985
      }
    }

    let time = 0
    const animate = () => {
      const { width, height } = dimensionsRef.current
      const dpr = window.devicePixelRatio || 1
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.clearRect(0, 0, width, height)

      time++

      drawOrbs(time)
      updateRipples()
      updateParticles(time)
      spawnTrailParticles()
      drawConnections(particles)

      for (const p of particles) {
        drawParticle(p, time)
      }

      drawMouseWeb(particles)
      drawRipples()
      drawTempNodes()
      drawTrail()
      drawVignette()

      animationRef.current = requestAnimationFrame(animate)
    }

    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect()
      mouseRef.current = { x: e.clientX - rect.left, y: e.clientY - rect.top }
    }

    const handleMouseLeave = () => {
      mouseRef.current = { x: -1000, y: -1000 }
    }

    const handleClick = (e) => {
      const rect = canvas.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      if (x >= 0 && x <= rect.width && y >= 0 && y <= rect.height) {
        spawnRipple(x, y)
      }
    }

    resize()
    animate()

    window.addEventListener('resize', resize)
    window.addEventListener('click', handleClick)
    canvas.addEventListener('mousemove', handleMouseMove)
    canvas.addEventListener('mouseleave', handleMouseLeave)

    return () => {
      window.removeEventListener('resize', resize)
      window.removeEventListener('click', handleClick)
      canvas.removeEventListener('mousemove', handleMouseMove)
      canvas.removeEventListener('mouseleave', handleMouseLeave)
      if (animationRef.current) cancelAnimationFrame(animationRef.current)
    }
  }, [theme])

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 pointer-events-auto ${className}`}
      aria-hidden="true"
    />
  )
}

export default ParticleNetwork
