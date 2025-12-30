import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Plus, Sparkle, Warning, Check, TrendUp, TrendDown, MinusCircle, CaretUpDown, Star } from '@phosphor-icons/react'
import { api } from '@/lib/api'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

export function ReviewDialog({ onReviewCreated, existingHospitals }) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [hospitalOpen, setHospitalOpen] = useState(false)
  const [formData, setFormData] = useState({
    hospital_name: '',
    hospital_address: '',
    review_text: '',
  })
  const [preview, setPreview] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!formData.review_text.trim()) {
      setPreview(null)
      return
    }

    const timeoutId = setTimeout(async () => {
      try {
        setAnalyzing(true)
        const analysis = await api.analyzeText(formData.review_text)
        setPreview(analysis)
      } catch (err) {
        setPreview(null)
      } finally {
        setAnalyzing(false)
      }
    }, 1000)

    return () => clearTimeout(timeoutId)
  }, [formData.review_text])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!formData.hospital_name.trim()) {
      setError('Hospital name is required')
      return
    }

    if (!formData.review_text.trim()) {
      setError('Review text is required')
      return
    }

    setLoading(true)

    try {
      await api.createReview(formData)
      toast.success('Review submitted successfully!', {
        description: 'Your review has been analyzed and published.',
      })
      setOpen(false)
      setFormData({ hospital_name: '', hospital_address: '', review_text: '' })
      setPreview(null)
      onReviewCreated()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit review')
      toast.error('Failed to submit review', {
        description: 'Please try again later.',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleHospitalSelect = (hospital) => {
    setFormData({
      ...formData,
      hospital_name: hospital.name,
      hospital_address: hospital.address,
    })
    setHospitalOpen(false)
  }

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-positive text-positive-foreground'
      case 'negative':
        return 'bg-negative text-negative-foreground'
      default:
        return 'bg-neutral text-neutral-foreground'
    }
  }

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return <TrendUp size={16} weight="bold" />
      case 'negative':
        return <TrendDown size={16} weight="bold" />
      default:
        return <MinusCircle size={16} weight="bold" />
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          size="lg"
          className="fixed bottom-6 right-6 h-14 px-6 rounded-full shadow-lg bg-accent hover:bg-accent/90 text-accent-foreground font-semibold z-50 md:relative md:bottom-auto md:right-auto md:h-auto"
        >
          <Plus size={20} weight="bold" className="mr-2" />
          Write Review
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Share Your Experience</DialogTitle>
          <DialogDescription>
            Help others by sharing your hospital experience. Your review will be analyzed for sentiment.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="hospital-name">
              Hospital Name <span className="text-destructive">*</span>
            </Label>
            <Popover open={hospitalOpen} onOpenChange={setHospitalOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  role="combobox"
                  aria-expanded={hospitalOpen}
                  className="w-full justify-between"
                  disabled={loading}
                >
                  {formData.hospital_name || "Select or type hospital name..."}
                  <CaretUpDown size={16} className="ml-2 shrink-0 opacity-50" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-full p-0" align="start">
                <Command>
                  <CommandInput 
                    placeholder="Search or type hospital name..." 
                    value={formData.hospital_name}
                    onValueChange={(value) => setFormData({ ...formData, hospital_name: value })}
                  />
                  <CommandList>
                    <CommandEmpty>
                      <div className="p-2 text-sm text-muted-foreground">
                        Type to add new hospital: "{formData.hospital_name}"
                      </div>
                    </CommandEmpty>
                    <CommandGroup heading="Existing Hospitals">
                      {existingHospitals && existingHospitals.map((hospital) => (
                        <CommandItem
                          key={hospital.name}
                          value={hospital.name}
                          onSelect={() => handleHospitalSelect(hospital)}
                        >
                          <Check
                            className={cn(
                              "mr-2",
                              formData.hospital_name === hospital.name ? "opacity-100" : "opacity-0"
                            )}
                            size={16}
                          />
                          <div>
                            <div className="font-medium">{hospital.name}</div>
                            {hospital.address && (
                              <div className="text-xs text-muted-foreground">{hospital.address}</div>
                            )}
                          </div>
                        </CommandItem>
                      ))}
                    </CommandGroup>
                  </CommandList>
                </Command>
              </PopoverContent>
            </Popover>
          </div>

          <div className="space-y-2">
            <Label htmlFor="hospital-address">Hospital Address (Optional)</Label>
            <Input
              id="hospital-address"
              placeholder="e.g., 123 Main St, City, State"
              value={formData.hospital_address}
              onChange={(e) => setFormData({ ...formData, hospital_address: e.target.value })}
              disabled={loading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="review-text">
              Your Review <span className="text-destructive">*</span>
            </Label>
            <Textarea
              id="review-text"
              placeholder="Share your experience with the hospital staff, facilities, treatment quality, etc."
              value={formData.review_text}
              onChange={(e) => setFormData({ ...formData, review_text: e.target.value })}
              disabled={loading}
              rows={6}
              className="resize-none"
            />
          </div>

          <AnimatePresence mode="wait">
            {analyzing && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <div className="animate-spin">
                    <Sparkle size={16} weight="fill" />
                  </div>
                  Analyzing sentiment...
                </div>
              </motion.div>
            )}

            {preview && !analyzing && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2, type: 'spring', stiffness: 200 }}
                className="overflow-hidden"
              >
                <div className="bg-secondary/50 rounded-lg p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <Sparkle size={18} weight="fill" className="text-primary" />
                    <span className="text-sm font-semibold">Preview Analysis</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={`${getSentimentColor(preview.sentiment)} flex items-center gap-1.5`}>
                      {getSentimentIcon(preview.sentiment)}
                      {preview.sentiment.charAt(0).toUpperCase() + preview.sentiment.slice(1)}
                      <span className="ml-1 font-mono">{preview.score.toFixed(2)}</span>
                    </Badge>
                  </div>
                  {preview.aspects.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {preview.aspects.map((aspect, idx) => (
                        <Badge
                          key={idx}
                          variant="outline"
                          className={`${getSentimentColor(aspect.sentiment)} border-0 text-xs flex items-center gap-1`}
                        >
                          {aspect.aspect}
                          {aspect.star_rating && (
                            <span className="flex items-center gap-0.5 ml-1">
                              <Star size={10} weight="fill" />
                              {aspect.star_rating}
                            </span>
                          )}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {error && (
            <Alert variant="destructive" className="animate-shake">
              <Warning size={18} />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={loading}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="flex-1 bg-primary hover:bg-primary/90"
            >
              {loading ? (
                <>
                  <div className="animate-spin mr-2">
                    <Sparkle size={18} weight="fill" />
                  </div>
                  Submitting...
                </>
              ) : (
                <>
                  <Check size={18} weight="bold" className="mr-2" />
                  Submit Review
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
